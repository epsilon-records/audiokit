import typer
from pathlib import Path
from typing import List, Optional, Annotated
from .plugins.base import manager
import requests
import json
from .utils import handle_api_error, handle_cli_error

app = typer.Typer(help="AudioKit Extensible CLI", pretty_exceptions_show_locals=False)
API_URL = "http://localhost:8000"  # Should be configurable

@app.callback()
def main():
    """AudioKit command line interface"""
    pass

@app.command()
def analyze_loudness(
    audio_file: Path = typer.Argument(..., exists=True),
    window_size: float = typer.Option(0.1, help="Analysis window in seconds")
):
    """Analyze dynamic range and loudness characteristics"""
    try:
        with open(audio_file, "rb") as f:
            response = requests.post(
                f"{API_URL}/analyze/loudness",
                files={"audio_file": f},
                params={"window_size": window_size}
            )
        
        if response.status_code == 200:
            data = response.json()
            visualize_loudness_curve(data['loudness'], data['window_size'])
        else:
            handle_api_error(response)
            
    except Exception as e:
        handle_cli_error(e)

@app.command()
def analyze_spectral(
    audio_file: Path = typer.Argument(..., exists=True),
    features: List[str] = typer.Option(["mfcc", "centroid"], "--feature", "-f",
                                      help="Spectral features to analyze"),
    output: Optional[Path] = typer.Option(None, "--output", "-o",
                                        help="Output file for results")
):
    """Perform comprehensive spectral analysis of audio file"""
    try:
        with open(audio_file, "rb") as f:
            response = requests.post(
                f"{API_URL}/analyze/spectral",
                files={"audio_file": f},
                params={"features": features}
            )
            
        if response.status_code == 200:
            data = response.json()
            if output:
                with open(output, "w") as f:
                    json.dump(data, f, indent=2)
                typer.echo(f"Results saved to {output}")
            else:
                display_spectral_results(data)
        else:
            handle_api_error(response)
            
    except Exception as e:
        handle_cli_error(e)

@app.command()
def stems_separate(
    audio_file: Annotated[
        Path,
        typer.Argument(..., exists=True, dir_okay=False, help="Audio file to separate")
    ]
):
    """Separate audio stems"""
    try:
        raise NotImplementedError("Stem separation not implemented")
    except Exception as e:
        handle_cli_error(e)

@app.command()
def track_match(
    fingerprint: Annotated[
        str,
        typer.Argument(..., help="Audio fingerprint to match")
    ]
):
    """Match audio fingerprint"""
    try:
        raise NotImplementedError("Track matching not implemented")
    except Exception as e:
        handle_cli_error(e)

@app.command()
def style_transfer(
    audio_file: Annotated[
        str,
        typer.Argument(..., help="Audio file to transform")
    ],
    target_style: Annotated[
        str,
        typer.Option(..., help="Target musical style")
    ]
):
    """Transfer musical style"""
    raise typer.BadParameter("Not implemented yet")

@app.command()
def lyric_compose(
    lyrics_file: Annotated[
        str,
        typer.Argument(..., help="Lyrics file for melody generation")
    ]
):
    """Generate melody from lyrics"""
    raise typer.BadParameter("Not implemented yet")

@app.command()
def predict_crowd(
    social_data: Annotated[
        str,
        typer.Argument(..., help="Social media data for prediction")
    ]
):
    """Predict crowd reaction"""
    raise typer.BadParameter("Not implemented yet")

@app.command()
def model_royalties(
    streaming_data: Annotated[
        str,
        typer.Argument(..., help="Streaming data for royalty modeling")
    ]
):
    """Model royalty distributions"""
    raise typer.BadParameter("Not implemented yet")

@app.command()
def plan_tour(
    tour_dates: Annotated[
        str,
        typer.Argument(..., help="Tour dates for optimization")
    ]
):
    """Optimize tour routing"""
    raise typer.BadParameter("Not implemented yet")

@app.command()
def forecast_trends(
    market_data: Annotated[
        str,
        typer.Argument(..., help="Market data for trend forecasting")
    ]
):
    """Forecast music trends"""
    raise typer.BadParameter("Not implemented yet")

@app.command()
def blend_styles(
    style1: Annotated[
        str,
        typer.Argument(..., help="First musical style")
    ],
    style2: Annotated[
        str,
        typer.Argument(..., help="Second musical style")
    ]
):
    """Blend musical styles"""
    raise typer.BadParameter("Not implemented yet")

@app.command()
def animate_cover(
    cover_art: Annotated[
        str,
        typer.Argument(..., help="Cover art file for animation")
    ]
):
    """Animate album artwork"""
    raise typer.BadParameter("Not implemented yet")

@app.command()
def create_nft(
    audio_file: Annotated[
        str,
        typer.Argument(..., help="Audio file for NFT creation")
    ]
):
    """Mint audio NFT"""
    raise typer.BadParameter("Not implemented yet")

@app.command()
def launch_remix(
    project_id: Annotated[
        str,
        typer.Argument(..., help="Project ID for remix collaboration")
    ]
):
    """Launch remix collaboration"""
    raise typer.BadParameter("Not implemented yet")

@app.command()
def bpm(
    audio_file: Annotated[
        Path,
        typer.Argument(..., exists=True, dir_okay=False, help="Audio file to analyze")
    ],
    method: Annotated[
        str,
        typer.Option("librosa", "--method", "-m", 
                     help="Tempo estimation algorithm",
                     case_sensitive=False)
    ] = "librosa"
):
    """Estimate audio tempo (BPM)"""
    try:
        with open(audio_file, "rb") as f:
            response = requests.post(
                f"{API_URL}/analyze/bpm",
                files={"audio_file": f},
                params={"method": method}
            )
            
        if response.status_code == 200:
            data = response.json()
            typer.echo(f"Estimated BPM: {data['bpm']:.2f} ({data['method']} method)")
        else:
            handle_api_error(response)
            
    except Exception as e:
        handle_cli_error(e)

@app.command()
def key(
    audio_file: Annotated[
        Path,
        typer.Argument(..., exists=True, dir_okay=False, help="Audio file to analyze")
    ],
    method: Annotated[
        str,
        typer.Option("krumhansl", "--method", "-m", 
                     help="Key detection algorithm",
                     case_sensitive=False)
    ] = "krumhansl"
):
    """Detect musical key of audio"""
    try:
        with open(audio_file, "rb") as f:
            response = requests.post(
                f"{API_URL}/analyze/key",
                files={"audio_file": f},
                params={"method": method}
            )
            
        if response.status_code == 200:
            data = response.json()
            typer.echo(f"Detected Key: {data['key']} (Confidence: {data['confidence']:.2%})")
        else:
            handle_api_error(response)
            
    except Exception as e:
        handle_cli_error(e)

@app.command()
def upload(
    file: Annotated[
        Path,
        typer.Argument(..., exists=True, dir_okay=False, 
                      help="Audio file to process",
                      # 200MB limit
                      max_content_size=200 * 1024 * 1024)
    ]
):
    """Upload audio file for processing"""
    try:
        with open(file, "rb") as f:
            response = requests.post(
                f"{API_URL}/upload",
                files={"file": f}
            )
            
        if response.status_code == 200:
            typer.echo("File uploaded successfully")
        else:
            handle_api_error(response)
            
    except Exception as e:
        handle_cli_error(e)

if __name__ == "__main__":
    app() 