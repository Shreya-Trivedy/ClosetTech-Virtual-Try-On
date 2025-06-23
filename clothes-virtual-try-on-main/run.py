import os
from PIL import Image
import shutil

def resize_img(path):
    im = Image.open(path)
    im = im.resize((768, 1024))
    im.save(path)

def try_on_model(model_path, cloth_path, output_path):
    # Define working directories
    base_dir = "working_dir"
    cloth_dir = os.path.join(base_dir, "inputs/test/cloth")
    model_dir = os.path.join(base_dir, "inputs/test/image")
    mask_dir = os.path.join(base_dir, "inputs/test/cloth-mask")
    output_dir = os.path.join(base_dir, "output")
    test_pairs_path = os.path.join(base_dir, "inputs/test_pairs.txt")

    # Clean previous inputs
    if os.path.exists(base_dir):
        shutil.rmtree(base_dir)
    os.makedirs(cloth_dir, exist_ok=True)
    os.makedirs(model_dir, exist_ok=True)

    # Copy and resize input images
    shutil.copy(cloth_path, cloth_dir)
    shutil.copy(model_path, model_dir)

    for path in os.listdir(cloth_dir):
        resize_img(os.path.join(cloth_dir, path))
    for path in os.listdir(model_dir):
        resize_img(os.path.join(model_dir, path))

    # Remove background from cloth
    os.system("python remove_bg.py")

    # Generate cloth mask
    os.system("python cloth-mask.py")

    # Run human parser
    os.system(
        "python Self-Correction-Human-Parsing/simple_extractor.py --dataset 'lip' "
        "--model-restore 'Self-Correction-Human-Parsing/checkpoints/final.pth' "
        f"--input-dir '{model_dir}' --output-dir '{base_dir}/inputs/test/image-parse'"
    )

    # Run OpenPose (assumes openpose is built & available)
    os.system(
        f"cd openpose && ./build/examples/openpose/openpose.bin "
        f"--image_dir ../{model_dir} "
        f"--write_json ../{base_dir}/inputs/test/openpose-json/ "
        f"--display 0 --render_pose 0 --hand"
    )
    os.system(
        f"cd openpose && ./build/examples/openpose/openpose.bin "
        f"--image_dir ../{model_dir} "
        f"--display 0 --write_images ../{base_dir}/inputs/test/openpose-img/ "
        f"--hand --render_pose 1 --disable_blending true"
    )

    # Prepare pair file
    model_img = os.listdir(model_dir)[0]
    cloth_img = os.listdir(cloth_dir)[0]
    with open(test_pairs_path, 'w') as file:
        file.write(f"{model_img} {cloth_img}")

    # Run virtual try-on
    os.system(
        f"python test.py --name output "
        f"--dataset_dir {base_dir}/inputs "
        f"--checkpoint_dir checkpoints "
        f"--save_dir {output_dir}"
    )

    # Copy result
    result_path = os.path.join(output_dir, "output", model_img)
    if os.path.exists(result_path):
        shutil.copy(result_path, output_path)
    else:
        raise Exception("Output image not generated.")

    # Clean up large intermediate files if needed
    # shutil.rmtree(base_dir)
