import os
import streamlit.components.v1 as components

# Declare the component
_component_func = components.declare_component(
    "elevenlabs_component",
    path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend/build"),
)

def elevenlabs_component(text: str):
    # Call the component with the provided arguments
    component_value = _component_func(text=text)
    return component_value
