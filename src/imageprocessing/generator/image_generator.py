"""Simian image generation web app."""

import os
import shutil
from pathlib import Path

import imageprocessing.generic
import imageprocessing.generator.image_gen_actions  # Import ensures Image gen actions are available.
from imageprocessing.parts.actions_list import apply_action, DOC, initialize_actions
import imageprocessing.parts.image_panel as image_comp
from simian.gui import Form, utils


def gui_init(_meta_data: dict) -> dict:
    """Initialize the app."""
    # Initialize components.
    Form.componentInitializer(
        actionGrid=initialize_actions(process_input_image=False),
        image_panel=image_comp.initialize_images(
            user_image_io=True, input_label="None", use_input_image=False
        ),
        description=extend_description,
    )
    form = Form(from_file=__file__)
    form.addCustomCss(imageprocessing.generic.get_css())

    return {
        "form": form,
        "navbar": {
            "title": "Image generation",
            "subtitle": "<small>Simian demo</small>",
            "logo": imageprocessing.generic.get_tasti_logo(),
        },
    }


def gui_event(meta_data: dict, payload: dict) -> dict:
    """Process app events."""
    Form.eventHandler(
        FileSelectionChange=image_comp.file_selection_change,
        ProcessFiles=process_files,
    )
    callback = utils.getEventFunction(meta_data, payload)
    return callback(meta_data, payload)


def extend_description(comp):
    """Append the description with the ImagePanel and ActionList DOCs."""
    comp.content = (comp.content + "\n" + image_comp.DOC + DOC).replace("\n", "<br>")


def process_files(meta_data: dict, payload: dict) -> dict:
    """Process the selected files."""
    # Prepare output locations.
    temp_target_folder = Path(utils.getSessionFolder(meta_data)) / "processed_temp"
    os.makedirs(temp_target_folder, exist_ok=True)

    # Get the full and relative path and extension of the image file.
    fig, _ = utils.getSubmissionData(payload, "imageName")
    name, ext = os.path.splitext(fig)
    if ext == "":
        ext = ".png"
        fig = name + ext

    # Prepare output locations.
    target_fig = str(temp_target_folder / fig)
    Path(target_fig).unlink(missing_ok=True)
    apply_action(payload, None, target_fig)

    # Put the created file in the ResultFile component for the user to download.
    image_comp.upload_and_show_figure(meta_data, payload, target_fig, fig)

    # Clear session folder to remove temp figures again.
    shutil.rmtree(temp_target_folder, ignore_errors=True)

    return payload
