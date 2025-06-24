import json
from datetime import datetime
from pathlib import Path

import typer
from cv2 import imwrite

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

    angle_data, bottom_frame, top_frame = analyze_video(
        video, output_dir / "annotated_video.mp4"
    )

    imwrite(str(output_dir / "stroke_top.jpg"), top_frame)
    imwrite(str(output_dir / "stroke_bottom.jpg"), bottom_frame)

    with open(output_dir / "angle_data.json", "w") as f:
        json.dump(angle_data, f, indent=2)

    suggestions: dict[str, str] = generate_fit_suggestions(angle_data)
    with open(output_dir / "suggestions.json", "w") as f:
        json.dump(suggestions, f, indent=2)

    typer.echo("📋 Summary of suggestions:")
    for k, v in suggestions.items():
        typer.echo(
            f" - {''.join([f'[{item.capitalize()}]' for item in k.split('_')])}: {v}"
        )

    typer.echo(f"✅ All bike-fit details saved to {output_dir}")
    db.close()
