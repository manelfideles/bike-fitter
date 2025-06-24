import json
from datetime import datetime
from pathlib import Path

import typer

from app.db import SessionLocal
from app.models.bike import Bike
from app.models.user import User
from app.utils.fitting_logic import generate_fit_suggestions
from app.utils.video_analysis import analyze_video

app = typer.Typer()


@app.command("analyze")
def analyze_fit(
    user_id: int = typer.Option(..., help="User ID"),
    bike_id: int = typer.Option(..., help="Bike ID"),
    video: Path = typer.Option(..., exists=True, file_okay=True, dir_okay=False),
):
    """
    Analyze a bike fit using a side-view video and output annotated video and fit suggestions.
    """
    db = SessionLocal()

    user = db.query(User).filter(User.id == user_id).first()
    bike = db.query(Bike).filter(Bike.id == bike_id).first()

    if not user:
        typer.echo(f"❌ User with ID {user_id} not found.")
        raise typer.Exit(1)
    if not bike:
        typer.echo(f"❌ Bike with ID {bike_id} not found.")
        raise typer.Exit(1)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path("bike-fits") / f"{user_id}_{bike_id}_{timestamp}"
    output_dir.mkdir(parents=True, exist_ok=True)

    typer.echo(f"✅ Created output directory: {output_dir}")
    typer.echo("🔄 Running video analysis and generating fit suggestions...")

    annotated_video_path = output_dir / "annotated_video.mp4"
    avg_angles = analyze_video(video, annotated_video_path)

    angles_path = output_dir / "joint_angles.json"
    with open(angles_path, "w") as f:
        json.dump(avg_angles, f, indent=2)

    suggestions: dict[str, str] = generate_fit_suggestions(
        avg_angles, user.riding_position
    )
    suggestions_path = output_dir / "fit_suggestions.json"
    with open(suggestions_path, "w") as f:
        json.dump(suggestions, f, indent=2)

    typer.echo(f"💡 Fit suggestions saved to: {suggestions_path}")
    typer.echo("📋 Summary of suggestions:")
    for k, v in suggestions.items():
        typer.echo(f" - {k.capitalize()}: {v}")

    typer.echo(f"✅ Annotated video saved to: {annotated_video_path}")
    typer.echo(f"📐 Joint angles saved to: {angles_path}")
    typer.echo(f"🎯 Average angles: {avg_angles}")
    db.close()
