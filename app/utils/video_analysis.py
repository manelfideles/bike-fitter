import pprint
from collections import defaultdict
from pathlib import Path
from typing import Union

import cv2
import mediapipe as mp
import numpy as np

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils


def get_coords_from_landmark(lm, i):
    return (lm[i].x, lm[i].y)


def calculate_angle(a, b, c):
    """
    Calculates angle at point 'b', given three 2D points.
    """
    a, b, c = np.array(a), np.array(b), np.array(c)
    ba = a - b
    bc = c - b
    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    angle = np.arccos(np.clip(cosine_angle, -1.0, 1.0))
    return np.degrees(angle)


def draw_angles_in_frame(angles: dict[str, str], frame: cv2.typing.MatLike):
    for i, (joint, angle) in enumerate(angles.items()):
        if angle is not None:
            text = f"{joint.capitalize()}: {int(angle)} degrees "
            cv2.putText(
                frame,
                text,
                (10, 30 + i * 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 0, 255),
                2,
                cv2.LINE_AA,
            )


def draw_landmarks_in_frame(landmarks, frame: cv2.typing.MatLike):
    mp_drawing.draw_landmarks(
        image=frame,
        landmark_list=landmarks,
        connections=mp_pose.POSE_CONNECTIONS,
        landmark_drawing_spec=mp_drawing.DrawingSpec(
            color=(0, 255, 0), thickness=2, circle_radius=2
        ),
        connection_drawing_spec=mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=2),
    )


def extract_joint_angles(landmarks):
    """Extract joint angles of interest from MediaPipe results."""
    angles = {}
    try:
        knee = get_coords_from_landmark(landmarks, mp_pose.PoseLandmark.LEFT_KNEE.value)
        hip = get_coords_from_landmark(landmarks, mp_pose.PoseLandmark.LEFT_HIP.value)
        shoulder = get_coords_from_landmark(
            landmarks, mp_pose.PoseLandmark.LEFT_SHOULDER.value
        )
        elbow = get_coords_from_landmark(
            landmarks, mp_pose.PoseLandmark.LEFT_ELBOW.value
        )
        ankle = get_coords_from_landmark(
            landmarks, mp_pose.PoseLandmark.LEFT_ANKLE.value
        )
        wrist = get_coords_from_landmark(
            landmarks, mp_pose.PoseLandmark.LEFT_WRIST.value
        )
        angles["knee"] = calculate_angle(hip, knee, ankle)
        angles["hip"] = calculate_angle(shoulder, hip, knee)
        angles["back"] = calculate_angle(hip, shoulder, (hip[0] + 1, hip[1]))
        angles["shoulder"] = calculate_angle(elbow, shoulder, hip)
        angles["elbow"] = calculate_angle(shoulder, elbow, wrist)
    except Exception:
        pass  # Invalid or missing landmarks
    return angles


def analyze_video(
    input_path: Path, output_path: Path
) -> tuple[dict[str, dict[str, float], cv2.typing.MatLike, cv2.typing.MatLike]]:
    cap = cv2.VideoCapture(str(input_path))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
    pose = mp_pose.Pose(
        static_image_mode=False,
        model_complexity=1,
        enable_segmentation=False,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    )
    knee_angles: list[tuple[int, float]] = []
    frames_data: list[dict[str, Union[dict, cv2.typing.MatLike]]] = []
    frame_idx = 0
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(image_rgb)
        draw_landmarks_in_frame(results.pose_landmarks, frame)
        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark
            angles: dict[str, str] = extract_joint_angles(landmarks)
            draw_angles_in_frame(angles, frame)
            knee = angles.get("knee")
            if knee:
                knee_angles.append((frame_idx, knee))
            frames_data.append({"angles": angles, "frame": frame})
        frame_idx += 1
        out.write(frame)
    cap.release()
    out.release()
    pose.close()

    bottom_idx, _ = max(knee_angles, key=lambda x: x[1])
    top_idx, _ = min(knee_angles, key=lambda x: x[1])
    top_angles, top_frame = (
        frames_data[top_idx]["angles"],
        frames_data[top_idx]["frame"],
    )
    bottom_angles, bottom_frame = (
        frames_data[bottom_idx]["angles"],
        frames_data[bottom_idx]["frame"],
    )
    angle_data = {"bottom": bottom_angles, "top": top_angles}
    return angle_data, bottom_frame, top_frame
