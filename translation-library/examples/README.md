# Examples

This directory contains example scripts demonstrating how to use the Eleven Labs TTS integration with the translation library.

## Files

### `quickstart_tts.py`
The simplest example to get started. Shows:
- Basic translate & speak functionality
- Batch generation in multiple languages
- Auto-play feature

**Run it:**
```bash
python examples/quickstart_tts.py
```

### `elevenlabs_tts_example.py`
Comprehensive example suite covering:
1. Basic text-to-speech without translation
2. Translate lyrics and generate audio
3. Generate audio in multiple languages
4. Using custom voices
5. Playing generated audio
6. Handling long lyrics
7. Checking API usage stats

**Run it:**
```bash
python examples/elevenlabs_tts_example.py
```

## Prerequisites

Before running the examples, make sure you have:

1. **Installed the library:**
   ```bash
   cd translation-library
   pip install -r requirements.txt
   ```

2. **Set your API keys:**
   ```bash
   export DEEPL_API_KEY="your-deepl-api-key"
   export ELEVENLABS_API_KEY="your-elevenlabs-api-key"
   ```

3. **(Linux only) Installed an audio player:**
   ```bash
   sudo apt-get install mpg123
   # or
   sudo apt-get install ffmpeg
   ```

## Quick Test

Run the quickstart example to verify everything is working:

```bash
# Set API keys
export DEEPL_API_KEY="your-key"
export ELEVENLABS_API_KEY="your-key"

# Run quickstart
python examples/quickstart_tts.py
```

This will:
- Translate "Hello, my friend" to Spanish
- Generate audio of the Spanish version
- Save it to `spanish_hello.mp3`
- Auto-play the audio
- Generate versions in French, German, Italian, and Japanese

## Output

The examples create several directories:
- `output/` - Audio files from individual examples
- `output/multilingual/` - Multi-language batch outputs
- `multilingual_output/` - Quickstart batch outputs

## Troubleshooting

**"No API key provided"**
- Make sure you've exported both API keys
- Or create a `.env` file in the translation-library directory

**"No audio player found" (Linux)**
- Install mpg123: `sudo apt-get install mpg123`

**Audio files created but can't play**
- Check that audio player is installed
- Try opening the MP3 files manually

## Next Steps

After running the examples:
1. Check the [TTS Guide](../ELEVENLABS_TTS_GUIDE.md) for detailed documentation
2. Explore voice options with `get_multilingual_voices()`
3. Experiment with voice parameters (stability, similarity, style)
4. Try translating your own lyrics!

## Support

For issues, refer to:
- [TTS Guide](../ELEVENLABS_TTS_GUIDE.md)
- [Main README](../README.md)
- [Eleven Labs Documentation](https://docs.elevenlabs.io/)