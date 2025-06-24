import json
from pathlib import Path

import cv2
import mediapipe as mp

from app.utils.compute_angles import calculate_angle

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils


def analyze_video(input_path: Path, output_path: Path) -> dict:
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
    frame_count = 0
    angle_totals = {"knee": 0, "hip": 0, "elbow": 0}
    angle_counts = {"knee": 0, "hip": 0, "elbow": 0}
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(image_rgb)
        if results.pose_landmarks:
            mp_drawing.draw_landmarks(
                frame,
                results.pose_landmarks,
                mp_pose.POSE_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=2),
            )
            angles: dict[str, str] = extract_joint_angles(results)
            for i, (joint, angle) in enumerate(angles.items()):
                if angle is not None:
                    position = (10, 30 + i * 30)
                    text = f"{joint.capitalize()}: {int(angle)} degrees "
                    cv2.putText(
                        frame,
                        text,
                        position,
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.8,
                        (0, 0, 255),
                        2,
                        cv2.LINE_AA,
                    )
                    angle_totals[joint] += angle
                    angle_counts[joint] += 1
        out.write(frame)
        frame_count += 1
    cap.release()
    out.release()
    pose.close()
    avg_angles = {
        joint: (
            round(angle_totals[joint] / angle_counts[joint], 1)
            if angle_counts[joint] > 0
            else None
        )
        for joint in angle_totals
    }
    return avg_angles


def extract_joint_angles(results):
    """Extract joint angles of interest from MediaPipe results."""
    lm = results.pose_landmarks.landmark
    get_coords = lambda i: (lm[i].x, lm[i].y)
    angles = {}
    try:
        # Left side (MediaPipe uses left/right from rider's POV)
        hip = get_coords(mp_pose.PoseLandmark.LEFT_HIP.value)
        knee = get_coords(mp_pose.PoseLandmark.LEFT_KNEE.value)
        ankle = get_coords(mp_pose.PoseLandmark.LEFT_ANKLE.value)
        shoulder = get_coords(mp_pose.PoseLandmark.LEFT_SHOULDER.value)
        elbow = get_coords(mp_pose.PoseLandmark.LEFT_ELBOW.value)
        wrist = get_coords(mp_pose.PoseLandmark.LEFT_WRIST.value)
        angles["knee"] = calculate_angle(hip, knee, ankle)
        angles["hip"] = calculate_angle(shoulder, hip, knee)
        angles["elbow"] = calculate_angle(shoulder, elbow, wrist)
    except Exception:
        pass  # Invalid or missing landmarks
    return angles
