.PHONY: film validate narration keyframes shots music assemble clean

# Default target: run the complete studio pipeline
film:
	python3 run_pipeline.py

# Stage-specific targets
validate:
	python3 pipeline/validate.py

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

# Clean intermediate assembly caches
clean:
	rm -rf outputs/final/temp_* outputs/final/concat_*

