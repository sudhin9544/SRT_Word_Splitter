# SRT Word Splitter

Convert an existing subtitle file into one SRT cue per word for editing in Premiere Pro or another SRT-compatible editor.

## Run it

Install Python 3. On Windows, open a terminal in this folder and run:

```powershell
py split_srt.py input.srt word-by-word.srt
```

On macOS or Linux, use `python3` in place of `py`. Use a new filename for the output. All processing runs locally, with no third-party Python packages.

## Timing and formatting

The tool divides each original cue's duration equally among its words and keeps the original cue boundaries. Word timing is approximate because the tool uses only the subtitle file. Review the result against the audio before publishing. Common text styling tags are removed, and punctuation stays with its word.
