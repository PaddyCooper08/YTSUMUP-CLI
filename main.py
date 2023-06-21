import typer

import threading

app = typer.Typer()
import api

from art import text2art

api.init()

title = "YT SUMUP"
artwork = text2art(title, font="block")

typer.secho(artwork, fg=typer.colors.RED)


@app.command()
def process_youtube_video(
    video_url: str = typer.prompt("Enter the YouTube video URL"),
    option: int = typer.prompt(
      "Choose an option: 1 (Short), 2 (Medium), 3 (Long), 4 (Custom)",
      type=int,
      default=1,
      show_choices=True,
      show_default=False,
    ),
    answer=typer.confirm("Would you like your summary to be grammar-checked?",
                         default=True)):

  api.answer = answer

  if option == 4:
    word_length = None
    while True:
      try:
        word_length = int(
          typer.prompt("Enter a word length for the custom option"))
        break
      except:
        typer.echo("Enter an integer!")

    typer.echo("Loading...")
    # Start the loading animation in a separate thread
    loading_thread = threading.Thread()
    loading_thread.start()
    api.process_video(video_url, option, word_length)

    # Wait for the process_video function to complete
    loading_thread.join()
    typer.echo("\rLoading... Done!")
  else:

    typer.echo("Loading...")
    # Start the loading animation in a separate thread
    loading_thread = threading.Thread()
    loading_thread.start()
    api.process_video(video_url, option, word_length=0)

    # Wait for the process_video function to complete
    loading_thread.join()
    typer.echo("\rLoading... Done!")


if __name__ == "__main__":
  app()
