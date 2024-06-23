import os
import streamlit.components.v1 as components

# Declare the AudioComponent
audio_component_func = components.declare_component(
    "audio_component",
    path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend/build"),
)

def audio_component(is_recording: bool):
    #print("audio_component called from __init__, is_recording: ", is_recording)
    # Call the component with the provided arguments
    component_value = audio_component_func(is_recording=is_recording)
    return component_value
