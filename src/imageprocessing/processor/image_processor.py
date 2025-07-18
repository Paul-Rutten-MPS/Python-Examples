"""Simian image processing web app.

Uses the Python Pillow library to modify images provided by the user.
"""

import os
import shutil
from pathlib import Path

import imageprocessing.generic
from imageprocessing.parts.actions_list import apply_action, initialize_actions
from imageprocessing.parts.image_panel import image_to_plotly, initialize_images
from simian.gui import Form, utils
from simian.gui.component import File, ResultFile


def gui_init(meta_data: dict) -> dict:
    """Initialize the app."""
    # Initialize components.
    Form.componentInitializer(
        actionGrid=initialize_actions(process_input_image=True),
        image_panel=initialize_images(user_image_io=True),
    )
    form = Form(from_file=__file__)
    form.addCustomCss(imageprocessing.generic.get_css())

    return {
        "form": form,
        "navbar": {
            "title": "Image processing",
            "subtitle": "<small>Simian demo</small>",
            "logo": imageprocessing.generic.get_tasti_logo(),
        },
    }


def gui_event(meta_data: dict, payload: dict) -> dict:
    """Process app events."""
    Form.eventHandler(
        FileSelectionChange=file_selection_change,
        ProcessFiles=process_files,
    )
    callback = utils.getEventFunction(meta_data, payload)
    return callback(meta_data, payload)


def file_selection_change(meta_data: dict, payload: dict) -> dict:
    """Process file selection change.

    When a figure is selected, show it in the app. Otherwise notify none selected.
    """
    payload, selected_figure = File.storeUploadedFiles(meta_data, payload, "inputFile")
    has_image = len(selected_figure) != 0
    utils.setSubmissionData(payload, "hasImage", has_image)

    if has_image:
        selected_figure = selected_figure[0]

    # Show the selected image in the input Plotly component.
    plot_obj, _ = utils.getSubmissionData(payload, "image")
    image_to_plotly(plot_obj, selected_figure)
    utils.setSubmissionData(payload, key="image", data=plot_obj)

    # Remove any images from the Result Plotly component.
    plot_obj, _ = utils.getSubmissionData(payload, "resultFigure")
    image_to_plotly(plot_obj, "")
    utils.setSubmissionData(payload, key="resultFigure", data=plot_obj)
    utils.setSubmissionData(payload, "hasResult", False)

    return payload


def process_files(meta_data: dict, payload: dict) -> dict:
    """Process the selected files."""
    # Prepare output locations.
    temp_target_folder = Path(utils.getSessionFolder(meta_data)) / "processed_temp"
    os.makedirs(temp_target_folder, exist_ok=True)

    # Get the full and relative path and extension of the image file.
    selected_figure, _ = utils.getSubmissionData(payload, "inputFile")
    full_fig = Path(utils.getSessionFolder(meta_data)) / selected_figure[0]["name"]
    name, ext = os.path.splitext(selected_figure[0]["originalName"])
    fig = name + "_mod_" + ext

    # Prepare output locations.
    target_fig = str(temp_target_folder / fig)
    Path(target_fig).unlink(missing_ok=True)
    apply_action(payload, full_fig, target_fig)

    # Put the created file in the ResultFile component for the user to download.
    if os.path.isfile(target_fig):
        ResultFile.upload(
            file_paths=[target_fig],
            mime_types=["image/*"],
            meta_data=meta_data,
            payload=payload,
            key="resultFile",
            file_names=[fig],
        )

        # Show the processed file in the web app.
        plot_obj, _ = utils.getSubmissionData(payload, "resultFigure")
        image_to_plotly(plot_obj, target_fig)
        utils.setSubmissionData(payload, "resultFigure", plot_obj)
        utils.setSubmissionData(payload, "hasResult", True)

    # Clear session folder to remove temp figures again.
    shutil.rmtree(temp_target_folder, ignore_errors=True)

    return payload
