.PHONY: film force smoke validate narration keyframes shots music assemble clean help

# Default target: compile and run complete studio pipeline
film:
	python3 run_pipeline.py

# Force regenerate all media assets ignoring cache
force:
	python3 run_pipeline.py --force

# Verification & Smoke tests
smoke:
	python3 pipeline/smoke_test.py

validate:
	python3 pipeline/validate.py

# Individual stage targets
narration:
	python3 pipeline/narration.py

keyframes:
	python3 pipeline/keyframes.py

shots:
	python3 pipeline/shots.py

music:
	python3 pipeline/music.py

assemble:
	python3 pipeline/assemble.py

# Clean temporary intermediate render artifacts
clean:
	rm -rf outputs/final/temp_* outputs/final/concat_* outputs/concat_shots.txt

# Help overview
help:
	@echo "AI-Content-Generation Studio Makefile Targets:"
	@echo "  make film       - Run the complete autonomous pipeline end-to-end"
	@echo "  make force      - Force regenerate all assets ignoring cache"
	@echo "  make validate   - Validate storyboard.json against schema"
	@echo "  make smoke      - Run API smoke tests for Gemini, Cloudflare & Kaggle"
	@echo "  make narration  - Generate Amharic voiceover & master radio cut"
	@echo "  make keyframes  - Generate FLUX.1 conditioned keyframes"
	@echo "  make shots      - Generate 1080p moving video shots"
	@echo "  make music      - Synthesize & audition ACE-Step score candidates"
	@echo "  make assemble   - Produce dual 9:16 and 16:9 master video exports"
