# prosthetic-sim

A MuJoCo-based hand prosthetic simulation that receives gesture classifications over WebSocket and visualizes them on the MyoHand musculoskeletal model (23 DOF, 39 muscles). Built for validating AI-classified gestures from an external model before deploying to hardware.

---

## What this does

- Loads the [MyoHand](https://github.com/MyoHub/myo_sim) model in MuJoCo
- Runs a WebSocket server locally (`ws://localhost:8765`)
- Your AI classifier sends a gesture name (e.g. `{"gesture": "c2_small_diameter"}`) and the hand moves to that pose in real time
- Includes 62 gestures covering the Ninapro DB1 exercise set (A, B, C, D + rest)
- Includes an interactive mock client to step through all gestures manually for validation

---

## Project structure

```
prosthetic-sim/
├── pyproject.toml
├── .python-version         # pins pyenv Python (3.12.13)
├── .env                    # MUJOCO_GL and WebSocket config
├── models/
│   └── myo_sim/            # cloned from MyoHub/myo_sim
├── envs/
│   ├── __init__.py
│   ├── hand_env.py         # MuJoCo env wrapper
│   └── gestures.py         # 62 gesture → muscle activation mappings
├── bridge/
│   ├── __init__.py
│   ├── ws_server.py        # WebSocket server (thread-safe queue)
│   └── mock_client.py      # interactive gesture test client
└── viz/
    ├── run_viewer.py       # main entry point
    └── record_video.py     # headless MP4 recording
```

---

## Setup — macOS (Apple Silicon or Intel)

### Why this is more involved than usual

MuJoCo's `mjpython` launcher — required on macOS to run the viewer — needs Python built as a **shared library** (`libpython3.12.dylib`). The Python bundled by `uv` is statically linked and doesn't have this file, so `mjpython` fails to `dlopen` it with an error like:

```
failed to dlopen: Library not loaded: @rpath/libpython3.12.dylib
```

The fix is to use `pyenv` to build Python with `--enable-shared`, and then point `uv` at that Python. You keep `uv` for dependency management — you just change where the Python binary comes from.

---

### Step 1 — Install Homebrew, pyenv, and build Python with shared libraries

```bash
# Install Homebrew if you don't have it
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install pyenv
brew install pyenv

# Add pyenv to your shell (add these lines to ~/.zshrc)
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"

# Reload shell
source ~/.zshrc

# Build Python 3.12.13 with shared library support — this flag is mandatory
PYTHON_CONFIGURE_OPTS="--enable-shared" pyenv install 3.12.13

# Verify the shared library was built (must print a path, not an error)
ls $(pyenv prefix 3.12.13)/lib/libpython3.12.dylib
```

If the `ls` command errors, the flag didn't take. Uninstall and retry:

```bash
pyenv uninstall 3.12.13
PYTHON_CONFIGURE_OPTS="--enable-shared" pyenv install 3.12.13
```

---

### Step 2 — Install uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.zshrc   # or open a new terminal
```

---

### Step 3 — Clone the repo and create the venv against pyenv's Python

```bash
git clone <your-repo-url> prosthetic-sim
cd prosthetic-sim

# Create .python-version pointing at pyenv's binary
echo "3.12.13" > .python-version

# Create the venv explicitly using pyenv's Python — not uv's bundled one
uv venv --python $(pyenv prefix 3.12.13)/bin/python3.12

# Verify it's using the right Python (should show a pyenv path, not ~/.local/share/uv)
.venv/bin/python -c "import sys; print(sys.executable)"
```

---

### Step 4 — Install dependencies

```bash
uv add mujoco gymnasium websockets numpy python-dotenv imageio
uv add --dev jupyter ipykernel
```

---

### Step 5 — Install the project as an editable package

This is required so that `mjpython` (which launches its own process) can find the `envs`, `bridge`, and `viz` packages. Without this step you get `ModuleNotFoundError: No module named 'envs'`.

Make sure your `pyproject.toml` contains:

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["envs", "bridge", "viz"]
```

Then install:

```bash
uv pip install -e .
```

---

### Step 6 — Configure environment

Create a `.env` file in the project root:

```bash
MUJOCO_GL=glfw
WS_HOST=localhost
WS_PORT=8765
```

---

### Step 7 — Run

Open two terminals, both from the project root 'simulation-frontend'.

**Terminal 1 — simulation viewer:**

```bash
# Must use the venv's mjpython, not the system one
.venv/bin/mjpython viz/run_viewer.py
```

You should see the MuJoCo viewer open with the hand model.

**Terminal 2 — mock client:**

```bash
uv run python bridge/mock_client.py
```

Press Enter to step through gestures, `p` to go back, `r` to reset to rest, type a number to jump to that gesture index, `q` to quit.

> **Why `.venv/bin/mjpython` and not just `mjpython`?**
> Running plain `mjpython` uses whichever one is on your system PATH — which may not be the one installed in your venv, and won't have access to your project's packages. Always use the venv-local binary. To save typing, add an alias to `~/.zshrc`:
> ```bash
> alias mjpy=".venv/bin/mjpython"
> ```

---

## Setup — Windows

> **Note:** MuJoCo supports Windows but `mjpython` is not available. The shared library issue described above does not apply. You use standard Python instead.

### Step 1 — Install Python 3.12

Download and install from [python.org](https://www.python.org/downloads/). During installation, check **"Add Python to PATH"**.

Verify:

```powershell
python --version   # should print 3.12.x
```

### Step 2 — Install uv

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Open a new terminal after installation.

### Step 3 — Clone and set up the project

```powershell
git clone <your-repo-url> prosthetic-sim
cd prosthetic-sim

uv venv --python python3.12
uv add mujoco gymnasium websockets numpy python-dotenv imageio
uv pip install -e .
```

### Step 4 — Configure `.env`

```
MUJOCO_GL=glfw
WS_HOST=localhost
WS_PORT=8765
```

### Step 5 — Run

**Terminal 1:**

```powershell
# On Windows, use python directly — mjpython is not needed
.venv\Scripts\python viz\run_viewer.py
```

**Terminal 2:**

```powershell
uv run python bridge\mock_client.py
```

---

## Connecting your AI model

Once the viewer is running, point your classifier at `ws://localhost:8765` and send JSON messages:

```json
{"gesture": "c2_small_diameter", "confidence": 0.94}
```

The server responds with:

```json
{"status": "ok", "gesture": "c2_small_diameter"}
```

### Gesture names

All 62 gestures from the Ninapro DB1 protocol:

| Key | Description |
|-----|-------------|
| `rest` | Rest position |
| `a1_index_flexion` | Index flexion |
| `a2_index_extension` | Index extension |
| `a3_middle_flexion` | Middle flexion |
| `a4_middle_extension` | Middle extension |
| `a5_ring_flexion` | Ring flexion |
| `a6_ring_extension` | Ring extension |
| `a7_little_flexion` | Little finger flexion |
| `a8_little_extension` | Little finger extension |
| `a9_thumb_adduction` | Thumb adduction |
| `a10_thumb_abduction` | Thumb abduction |
| `a11_thumb_flexion` | Thumb flexion |
| `a12_thumb_extension` | Thumb extension |
| `b1_thumb_up` | Thumb up |
| `b2_index_middle_ext` | Extension of index and middle, flexion of others |
| `b3_ring_little_flex` | Flexion of ring and little, extension of others |
| `b4_thumb_opp_little` | Thumb opposing base of little finger |
| `b5_all_abduction` | Abduction of all fingers |
| `b6_fist` | Fingers flexed together in fist |
| `b7_pointing` | Pointing index |
| `b8_adduction_extended` | Adduction of extended fingers |
| `b9_wrist_sup_mid` | Wrist supination (axis: middle finger) |
| `b10_wrist_pro_mid` | Wrist pronation (axis: middle finger) |
| `b11_wrist_sup_little` | Wrist supination (axis: little finger) |
| `b12_wrist_pro_little` | Wrist pronation (axis: little finger) |
| `b13_wrist_flexion` | Wrist flexion |
| `b14_wrist_extension` | Wrist extension |
| `b15_wrist_radial` | Wrist radial deviation |
| `b16_wrist_ulnar` | Wrist ulnar deviation |
| `b17_wrist_ext_closed` | Wrist extension with closed hand |
| `c1_large_diameter` | Large diameter grasp |
| `c2_small_diameter` | Small diameter grasp (power grip) |
| `c3_fixed_hook` | Fixed hook grasp |
| `c4_index_ext_grasp` | Index finger extension grasp |
| `c5_medium_wrap` | Medium wrap |
| `c6_ring_grasp` | Ring grasp |
| `c7_prismatic_four` | Prismatic four fingers grasp |
| `c8_stick_grasp` | Stick grasp |
| `c9_writing_tripod` | Writing tripod grasp |
| `c10_power_sphere` | Power sphere grasp |
| `c11_three_finger_sphere` | Three finger sphere grasp |
| `c12_precision_sphere` | Precision sphere grasp |
| `c13_tripod` | Tripod grasp |
| `c14_prismatic_pinch` | Prismatic pinch grasp |
| `c15_tip_pinch` | Tip pinch grasp |
| `c16_quadpod` | Quadpod grasp |
| `c17_lateral` | Lateral grasp |
| `c18_parallel_ext` | Parallel extension grasp |
| `c19_extension_type` | Extension type grasp |
| `c20_power_disk` | Power disk grasp |
| `c21_bottle_tripod` | Open a bottle with a tripod grasp |
| `c22_screw_stick` | Turn a screw (stick grasp) |
| `c23_cut_knife` | Cut something (index finger extension grasp) |
| `d1_little_flex` | Flexion of the little finger |
| `d2_ring_flex` | Flexion of the ring finger |
| `d3_middle_flex` | Flexion of the middle finger |
| `d4_index_flex` | Flexion of the index finger |
| `d5_thumb_abd` | Abduction of the thumb |
| `d6_thumb_flex` | Flexion of the thumb |
| `d7_index_little_flex` | Flexion of index and little finger |
| `d8_ring_middle_flex` | Flexion of ring and middle finger |
| `d9_index_thumb_flex` | Flexion of index finger and thumb |

---

## MuJoCo viewer controls

| Action | Input |
|--------|-------|
| Rotate | Left click + drag |
| Pan (move camera center) | Right click + drag |
| Zoom | Scroll wheel |
| Reset camera | Double click |

---

[//]: # (## Troubleshooting)

[//]: # ()
[//]: # (### `failed to dlopen libpython3.12.dylib` &#40;macOS&#41;)

[//]: # ()
[//]: # (You're using uv's bundled Python, which is statically linked. Fix: rebuild your venv against pyenv's Python built with `--enable-shared`. See Step 1–3 above.)

[//]: # ()
[//]: # (### `mjpython` not found in `.venv/bin/`)

[//]: # ()
[//]: # (`mjpython` is installed as part of the `mujoco` Python package. If it's missing, reinstall:)

[//]: # ()
[//]: # (```bash)

[//]: # (uv pip install mujoco --force-reinstall)

[//]: # (ls .venv/bin/mjpython)

[//]: # (```)

[//]: # ()
[//]: # (### `ModuleNotFoundError: No module named 'envs'`)

[//]: # ()
[//]: # (You're running `mjpython` without the project installed as a package. Run:)

[//]: # ()
[//]: # (```bash)

[//]: # (uv pip install -e .)

[//]: # (```)

[//]: # ()
[//]: # (And make sure `pyproject.toml` has the `[tool.hatch.build.targets.wheel]` section with `packages = ["envs", "bridge", "viz"]`.)

[//]: # ()
[//]: # (### `ValueError: Unable to determine which files to ship inside the wheel`)

[//]: # ()
[//]: # (Hatchling can't find a directory matching your project name. Add to `pyproject.toml`:)

[//]: # ()
[//]: # (```toml)

[//]: # ([tool.hatch.build.targets.wheel])

[//]: # (packages = ["envs", "bridge", "viz"])

[//]: # (```)

[//]: # ()
[//]: # (### `ModuleNotFoundError: No module named 'gymnasium'` when running `mjpython`)

[//]: # ()
[//]: # (You're calling the wrong `mjpython`. Use `.venv/bin/mjpython`, not the one on your system PATH.)

[//]: # ()
[//]: # (### Segmentation fault after a few gestures)

[//]: # ()
[//]: # (This happens if `mj_step` is called from the WebSocket background thread instead of the main thread. MuJoCo's viewer on macOS requires all physics calls to happen on the main thread. The `ws_server.py` should only call `env.request_gesture&#40;&#41;` &#40;which enqueues&#41;, never `env.set_gesture&#40;&#41;` directly. The render loop in `run_viewer.py` drains the queue via `env.apply_pending&#40;&#41;` on the main thread.)

[//]: # ()
[//]: # (### `ParseXML: Error opening file myohand.xml`)

[//]: # ()
[//]: # (Path mismatch. Check exactly what folder name you cloned into:)

[//]: # ()
[//]: # (```bash)

[//]: # (ls models/)

[//]: # (```)

[//]: # ()
[//]: # (Then match it in `envs/hand_env.py`:)

[//]: # ()
[//]: # (```python)

[//]: # (MODEL_PATH = Path&#40;__file__&#41;.parent.parent / "models" / "myo_sim" / "hand" / "myohand.xml")

[//]: # (```)

[//]: # ()
[//]: # (### `dependency conflict: myosuite` with `numpy>=2` or `mujoco>=3`)

[//]: # ()
[//]: # (MyoSuite pins old versions of mujoco &#40;2.3.x&#41; and numpy &#40;<2.0&#41;, which conflict with modern installs. The solution is to not install MyoSuite as a Python package — instead, clone the model files directly from [MyoHub/myo_sim]&#40;https://github.com/MyoHub/myo_sim&#41; and use MuJoCo directly. This project does exactly that.)

[//]: # ()
[//]: # (### `could not broadcast input array from shape &#40;40,&#41; into shape &#40;39,&#41;`)

[//]: # ()
[//]: # (A gesture array in `gestures.py` has 40 values but the MyoHand has 39 actuators. Either trim the array, or use `np.resize&#40;action, self.model.nu&#41;` in `hand_env.py` to clip automatically.)

[//]: # ()
[//]: # (### WebSocket connection closes immediately)

[//]: # ()
[//]: # (The server crashed on the previous message &#40;usually the shape mismatch above&#41; and dropped the connection. Fix the underlying error and reconnect.)

[//]: # ()
[//]: # (---)

[//]: # ()
[//]: # (## Recording a video)

[//]: # ()
[//]: # (To record a gesture sequence to MP4 without opening the viewer window:)

[//]: # ()
[//]: # (```bash)

[//]: # (uv run python viz/record_video.py)

[//]: # (```)

[//]: # ()
[//]: # (This uses offscreen rendering &#40;`MUJOCO_GL=osmesa`&#41;. Output is saved to `output.mp4`.)

[//]: # ()
[//]: # (---)

## License

Model files in `models/myo_sim/` are from [MyoHub/myo_sim](https://github.com/MyoHub/myo_sim) and licensed under Apache 2.0.