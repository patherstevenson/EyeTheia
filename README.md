# EyeTheia

## Overview

**EyeTheia** is an open-source, cross-platform toolbox for **webcam-based 2D gaze estimation**.

The project predicts the user's **point of regard on the screen** using facial images, facial landmarks, and deep learning-based gaze estimation models derived from the iTracker architecture.

EyeTheia combines:

* Deep learning-based gaze estimation
* Personalized calibration
* User-specific model adaptation
* Real-time gaze prediction
* Browser-side deployment through ONNX Runtime Web
* Python and client-server inference modes
* Reproducible research workflows

The toolbox was designed to provide an accessible alternative to dedicated eye-tracking hardware while remaining suitable for scientific research and experimental studies.

EyeTheia can be used in:

* Human-computer interaction research
* Cognitive science experiments
* Psychology studies
* Behavioral analysis
* Online experiments
* Laboratory experiments

Unlike dedicated eye trackers, EyeTheia only requires a standard webcam and commodity hardware.

---

# Key Features

## Personalized Calibration

EyeTheia includes a user-specific calibration procedure.

During calibration, participants fixate a set of predefined screen locations.

For each calibration point, the framework collects:

* Webcam images
* Facial landmarks
* Ground-truth screen coordinates

These samples are then used to adapt the gaze estimation model to the current participant.

This personalization step significantly improves prediction accuracy compared to a generic model.

---

## Browser Deployment with ONNX

A major feature of EyeTheia is its ability to deploy personalized gaze estimation models directly inside a web browser.

After calibration and model adaptation, EyeTheia can export the trained model to ONNX and execute it locally using ONNX Runtime Web. The exported ONNX model corresponds to the personalized gaze model obtained after calibration and fine-tuning.

This architecture provides:

* Real-time gaze estimation
* Reduced latency
* Improved privacy
* Lower server requirements
* Large-scale online deployment

The ONNX deployment remains fully compatible with the Python implementation and serves as an additional deployment option rather than a replacement.

---

## Deep Learning-Based Gaze Estimation

EyeTheia is based on the iTracker architecture introduced in:

> [Eye Tracking for Everyone, K. Krafka et al.](https://arxiv.org/abs/1606.05814)

![](./images/model.png)

The model combines:

* Face image
* Left eye image
* Right eye image
* Face grid

to estimate the user's gaze position directly in screen coordinates.

Predictions are returned as:

```text
(x, y) pixels
```

---

# Architecture

```text
Webcam
   │
   ▼
Face Detection / Landmark Extraction
   │
   ▼
Feature Extraction
   │
   ▼
EyeTheia Gaze Model
   │
   ├── PyTorch Inference
   ├── Client-Server Inference
   └── ONNX Browser Inference
   │
   ▼
Screen Gaze Coordinates
```

The framework is designed to remain independent of the landmark extraction backend and can be integrated with different computer vision pipelines.

---

# Repository Structure

```text
EyeTheia/
├── dataset/
├── figures/
├── images/
├── logs/
│   ├── assessments/
│   └── beta_search/
├── notebooks/
├── sourcedoc/
├── src/
│   ├── models/
│   ├── routes/
│   ├── tracker/
│   └── utils/
├── tests/
├── requirements.txt
├── Makefile
└── README.md
```

---

# Platform Compatibility

EyeTheia has been tested on:

* Ubuntu Linux
* Microsoft Windows

The toolbox is designed to be platform-independent and relies primarily on Python and PyTorch.

---

# Environment Setup

EyeTheia uses Python 3.10.

Create and activate a Conda environment:

```bash
conda create -n eyetheia python=3.10
conda activate eyetheia
```

Install dependencies:

```bash
make lib
```

This command installs dependencies from `requirements.txt` and the PyTorch version used during development.

---

# Hardware Requirements

## Minimum Requirements

* Standard webcam
* Python 3.10
* 8 GB RAM
* CPU inference support

## Recommended Requirements

* NVIDIA GPU with CUDA support
* 16 GB RAM or more
* Modern webcam

A dedicated GPU is not required for inference and experimentation but can significantly accelerate training and fine-tuning.

---

# Running EyeTheia

## Demo

```bash
make run
```

Equivalent command:

```bash
python3 src/main.py
```

## Baseline Model Server

```bash
make baseline
```

Equivalent command:

```bash
python src/run_server.py --model_path itracker_baseline.tar
```

## MPIIFaceGaze Model Server

```bash
make mpii
```

Equivalent command:

```bash
python src/run_server.py --model_path itracker_mpiiface.tar
```

---

# Pretrained Models

Pretrained checkpoints are available in:

```text
src/models/
```

Available models:

| Model                 | Description                   |
| --------------------- | ----------------------------- |
| itracker_baseline.tar | Baseline iTracker model       |
| itracker_mpiiface.tar | MPIIFaceGaze retrained model  |

---

# Calibration Workflow

EyeTheia includes built-in calibration procedures and calibration layouts.

Examples are available in:

```text
src/utils/calib_5/
src/utils/calib_9/
src/utils/calib_13/
```

The default workflow consists of:

1. Displaying calibration targets.
2. Capturing webcam images.
3. Extracting facial landmarks.
4. Associating visual features with known gaze coordinates.
5. Fine-tuning the gaze estimation model.

---

## Custom Calibration Interfaces

EyeTheia is not restricted to the built-in calibration layouts.

External applications may implement their own calibration interfaces and submit calibration samples directly to the EyeTheia backend.

This allows EyeTheia to be integrated into:

* Web-based experimental platforms
* Online behavioral studies
* Custom research software
* Third-party user interfaces

A typical workflow is:

```text
Custom Calibration UI
        │
        ▼
Calibration Samples
        │
        ▼
EyeTheia Backend
        │
        ▼
Model Fine-Tuning
        │
        ▼
Personalized Gaze Model
```

The backend exposes routes for:

* Screen configuration
* Calibration sample submission
* Model adaptation and fine-tuning
* Gaze prediction
* Personalized ONNX model export

Researchers may therefore implement their own calibration layouts and experimental interfaces while still relying on EyeTheia for model adaptation, personalized calibration, and gaze estimation.

This architecture allows researchers to design their own calibration procedures while still leveraging EyeTheia's adaptation and gaze estimation pipeline.

---

# Personalized Model Deployment

After calibration and fine-tuning, EyeTheia produces a personalized gaze estimation model.

Users may then choose between two deployment strategies:

* WebSocket/API inference through the Python backend.
* Browser-side deployment through ONNX Runtime Web.

The same personalized model can therefore be used either server-side or directly inside a web browser.

## WebSocket Prediction

The personalized model can remain hosted inside the Python backend.

In this configuration:

1. The client captures webcam frames and landmarks.
2. Features are sent to the EyeTheia backend.
3. The personalized model performs inference.
4. Predicted gaze coordinates are returned through the prediction API or WebSocket interface.

This mode is particularly useful when GPU resources are available on the server.

Relevant files:

```text
src/run_server.py
src/routes/ws_calibration.py
src/routes/ws_model.py
src/utils/ws_codec.py
```

---

## ONNX Browser Deployment

The personalized model can also be exported to ONNX.

The exported ONNX model corresponds to the personalized gaze model obtained after calibration and fine-tuning and can therefore be deployed independently of the Python backend.

Once exported, the model can be executed directly in the browser using ONNX Runtime Web.

This architecture provides:

* Real-time gaze estimation
* Reduced latency
* Improved privacy
* Reduced backend load
* Offline inference after calibration

Typical workflow:

```text
Calibration
      │
      ▼
Fine-Tuning
      │
      ▼
Personalized Model
      │
      ├──────────────┐
      ▼              ▼
WebSocket       ONNX Export
Inference            │
                     ▼
           ONNX Runtime Web
                     │
                     ▼
            Browser Prediction
```

Relevant file:

```text
src/routes/onnx.py
```

---

# Datasets

## GazeCapture

Original iTracker dataset.

Paper:

https://arxiv.org/abs/1606.05814

---

## MPIIFaceGaze

Desktop webcam gaze estimation dataset.

Dataset:

http://datasets.d2.mpi-inf.mpg.de/MPIIGaze/MPIIFaceGaze.zip

Place the dataset in:

```text
dataset/
```

For inference using pretrained checkpoints, downloading the dataset is not required.

For training or reproducing training experiments, the dataset must be downloaded and prepared.

---

# Experiments and Reproducibility

This repository contains the code, pretrained models, notebooks, logs, and analysis scripts used to generate the results reported in:

> [EyeTheia: A Lightweight and Accessible Eye-Tracking Toolbox](https://arxiv.org/abs/2601.06279)

accepted at ICPR 2026.

---

## Training and Calibration Experiments

### Training Pipeline

The MPIIFaceGaze model used throughout the paper was trained using the EyeTheia training pipeline located in:

```text
src/main_train.py
src/tracker/GazeTrain.py
src/tracker/GazeModel.py
src/utils/mpiifacegaze_dataset.py
```

The repository also includes the SLURM script used to execute the Huber loss hyperparameter search on a computing cluster:

```text
cluster_HuberLoss_beta_gridsearch.slurm
```

This script was used to perform the beta search reported in Section 5.1 and generate the training logs stored in:

```text
logs/beta_search/
```

The resulting model corresponds to the MPIIFaceGaze checkpoint distributed with the repository:

```text
src/models/itracker_mpiiface.tar
```

The complete training workflow is therefore:

```text
MPIIFaceGaze Dataset
          │
          ▼
src/main_train.py
          │
          ▼
cluster_HuberLoss_beta_gridsearch.slurm
          │
          ▼
logs/beta_search/
          │
          ▼
Training Figures (Section 5.1)
          │
          ▼
itracker_mpiiface.tar
```

The training and calibration results reported in Section 5.1 are supported by:

```text
logs/beta_search/
```

This directory contains:

```text
best_val_loss.csv
lr_comparison_beta_08.csv
summary_val_loss.csv
generate_plot.py
```

These files were used to generate the validation and training figures reported in the paper.

To regenerate the plots:

```bash
cd logs/beta_search
python generate_plot.py
```

Generated figures correspond to:

```text
figures/
├── fig_all_val_curves.png
├── fig_best_val_loss.png
├── fig_lr_comparison_beta_08.png
└── fig_val_curves_per_beta.png
```

Additional figures are available in:

```text
notebooks/figures/
```

The main training notebook example is:

```text
notebooks/iTracker_MPIIFace_Training.ipynb
```

---

### Experimental Data

The training figures reported in Section 5.1 were generated from the training logs stored in:

```text
logs/beta_search/
```

The comparison figures reported in Section 5.2 were generated from the experimental databases stored in:

```text
logs/assessments/db/
```

All scripts required to regenerate these figures are included in the repository.

## EyeTheia vs SeeSo Comparison

The comparison between EyeTheia and SeeSo reported in Section 5.2 is supported by:

```text
logs/assessments/
```

Contents:

```text
db/
function.py
interpret.ipynb
```

The `db/` directory contains the experimental recordings collected during the attentional bias dot-probe experiment using IAPS stimuli.

The notebook:

```text
logs/assessments/interpret.ipynb
```

and helper script:

```text
logs/assessments/function.py
```

were used to process the experimental databases and generate the EyeTheia vs SeeSo comparison figures reported in the paper.

To reproduce the analysis:

```bash
jupyter notebook logs/assessments/interpret.ipynb
```

Run all notebook cells to regenerate the reported figures.

---

# Experimental Platform

EyeTheia can be integrated into external experimental platforms.

The reference platform used in our studies is:

[Calypso Experimental Platform: Medita](https://git.interactions-team.fr/INTERACTIONS/calypso/src/branch/main/src/medita)

Calypso provides:

* Experimental task management
* Calibration interfaces
* Data collection workflows
* Online behavioral experiments

Within this framework, EyeTheia serves as the gaze estimation component.

---

# Documentation

The source documentation is located in:

```text
sourcedoc/
```

Build the HTML documentation:

```bash
make doc
```

Generated documentation will be available in:

```text
doc/
```

---

# Testing

Unit tests are available in:

```text
tests/
```

Run all tests:

```bash
make test
```

The test suite covers:

* Calibration
* Gaze tracking
* Model behavior
* Data logging
* Utility functions

---

# License

This project is licensed under the GNU General Public License v3.0 (GPL-3.0).

See:

```text
LICENSE
```

for details.

---

# Citation

If you use EyeTheia in your research, please cite:

```bibtex
@inproceedings{pather2026eyetheia,
  title     = {EyeTheia: A Lightweight and Accessible Eye-Tracking Toolbox},
  author    = {Pather, Stevenson and Maia, Deise Santana},
  booktitle = {International Conference on Pattern Recognition (ICPR)},
  year      = {2026}
}
```

Please update this entry with the final proceedings information once available.
