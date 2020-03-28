.PHONY: all
all: junebug

.PHONY: clean
clean:
	rm *.png *.json

%: %.ase 
	aseprite -b $< --list-tags --format json-array --data $@.json --sheet $@.png
	convert $@.png -alpha off $@.png
	aseprite -b --oneframe --sheet $@.icon.png --ignore-empty $< >/dev/null
	convert $@.icon.png -transparent 'rgb(255,0,255)' $@.icon.png
