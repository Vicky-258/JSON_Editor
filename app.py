import streamlit as st
import json
from pathlib import Path

DATASET_FILE = "dataset.json"

# =====================================
# Load Dataset
# =====================================

if Path(DATASET_FILE).exists():
    with open(DATASET_FILE, "r") as f:
        dataset = json.load(f)
else:
    dataset = []

# =====================================
# Helpers
# =====================================

def save_dataset():
    with open(DATASET_FILE, "w") as f:
        json.dump(dataset, f, indent=4)


def export_jsonl():
    with open("dataset.jsonl", "w") as f:
        for entry in dataset:
            f.write(json.dumps(entry) + "\n")

def delete_entry(index):
    dataset.pop(index)

    # Reassign sample IDs
    for i, entry in enumerate(dataset):
        entry["sample_id"] = i + 1

    save_dataset()


def update_entry(index, updated_entry):
    dataset[index] = updated_entry
    save_dataset()


def clear_dataset():
    dataset.clear()
    save_dataset()


# =====================================
# Session State Defaults
# =====================================

defaults = {
    "source_chunk_id": "",
    "source_text": "",
    "expected_text": "",
    "actual_text": "",
    "variant_type": "paraphrase",
    "similarity_score": 0.5,
    "label": "good_alignment"
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# =====================================
# Sidebar
# =====================================

st.sidebar.title("Dataset Info")

st.sidebar.metric(
    "Total Entries",
    len(dataset)
)

st.sidebar.divider()

# =====================================
# Export
# =====================================

st.sidebar.subheader("Export")

if st.sidebar.button("Export JSONL"):
    export_jsonl()
    st.sidebar.success("dataset.jsonl exported!")

st.sidebar.divider()

# =====================================
# Clear Dataset
# =====================================

st.sidebar.subheader("Danger Zone")

if st.sidebar.button("Clear Entire Dataset"):
    clear_dataset()
    st.sidebar.success("Dataset cleared!")
    st.rerun()

st.sidebar.divider()

# =====================================
# Entry Navigator
# =====================================

st.sidebar.subheader("Entry Navigator")

if dataset:

    selected_index = st.sidebar.selectbox(
        "Select Entry",
        range(len(dataset)),
        format_func=lambda x:
            f"#{dataset[x]['sample_id']} - {dataset[x]['label']}"
    )

    selected_entry = dataset[selected_index]

else:
    selected_index = None

# =====================================
# Main UI
# =====================================

st.title("NLP Dataset Annotation Tool")

with st.form("annotation_form"):

    st.text_input(
        "Source Chunk ID",
        key="source_chunk_id"
    )

    st.text_area(
        "Source Text",
        height=180,
        key="source_text"
    )

    st.text_area(
        "Expected Text",
        height=150,
        key="expected_text"
    )

    st.text_area(
        "Actual Text",
        height=150,
        key="actual_text"
    )

    st.selectbox(
        "Variant Type",
        [
            "paraphrase",
            "omission",
            "vague_summary",
            "weak_drift",
            "off_topic"
        ],
        key="variant_type"
    )

    st.slider(
        "Similarity Score",
        0.0,
        1.0,
        step=0.05,
        key="similarity_score"
    )

    st.selectbox(
        "Label",
        [
            "good_alignment",
            "partial_alignment",
            "weak_alignment",
            "off_topic"
        ],
        key="label"
    )

    submitted = st.form_submit_button("Save Entry")

# =====================================
# Save Logic
# =====================================

if submitted:

    entry = {
        "sample_id": len(dataset) + 1,
        "source_chunk_id": st.session_state.source_chunk_id,
        "source_text": st.session_state.source_text,
        "expected_text": st.session_state.expected_text,
        "actual_text": st.session_state.actual_text,
        "variant_type": st.session_state.variant_type,
        "similarity_score": st.session_state.similarity_score,
        "label": st.session_state.label
    }

    dataset.append(entry)

    save_dataset()

    st.success(
        f"Saved sample #{entry['sample_id']}"
    )

    # =====================================
    # AUTO CLEAR FORM
    # =====================================

    st.session_state.clear_form = True
    st.rerun()

# =====================================
# Latest Entry Preview
# =====================================

if dataset:

    st.divider()

    st.subheader("Latest Entry")

    st.json(dataset[-1])

# =====================================
# Entry Editor
# =====================================

if dataset and selected_index is not None:

    st.divider()

    st.subheader("Edit Entry")

    with st.form("edit_form"):

        edit_source_chunk_id = st.text_input(
            "Edit Source Chunk ID",
            value=selected_entry["source_chunk_id"]
        )

        edit_source_text = st.text_area(
            "Edit Source Text",
            value=selected_entry["source_text"],
            height=180
        )

        edit_expected_text = st.text_area(
            "Edit Expected Text",
            value=selected_entry["expected_text"],
            height=150
        )

        edit_actual_text = st.text_area(
            "Edit Actual Text",
            value=selected_entry["actual_text"],
            height=150
        )

        edit_variant_type = st.selectbox(
            "Edit Variant Type",
            [
                "paraphrase",
                "omission",
                "vague_summary",
                "weak_drift",
                "off_topic"
            ],
            index=[
                "paraphrase",
                "omission",
                "vague_summary",
                "weak_drift",
                "off_topic"
            ].index(selected_entry["variant_type"])
        )

        edit_similarity_score = st.slider(
            "Edit Similarity Score",
            0.0,
            1.0,
            value=float(selected_entry["similarity_score"]),
            step=0.05
        )

        edit_label = st.selectbox(
            "Edit Label",
            [
                "good_alignment",
                "partial_alignment",
                "weak_alignment",
                "off_topic"
            ],
            index=[
                "good_alignment",
                "partial_alignment",
                "weak_alignment",
                "off_topic"
            ].index(selected_entry["label"])
        )

        col1, col2 = st.columns(2)

        with col1:
            save_edit = st.form_submit_button("Save Changes")

        with col2:
            delete_edit = st.form_submit_button("Delete Entry")

    # =====================================
    # SAVE EDIT
    # =====================================

    if save_edit:

        updated_entry = {
            "sample_id": selected_entry["sample_id"],
            "source_chunk_id": edit_source_chunk_id,
            "source_text": edit_source_text,
            "expected_text": edit_expected_text,
            "actual_text": edit_actual_text,
            "variant_type": edit_variant_type,
            "similarity_score": edit_similarity_score,
            "label": edit_label
        }

        update_entry(selected_index, updated_entry)

        st.success("Entry updated!")

        st.rerun()

    # =====================================
    # DELETE ENTRY
    # =====================================

    if delete_edit:

        delete_entry(selected_index)

        st.warning("Entry deleted!")

        st.rerun()