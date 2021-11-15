# README

A small tool to pull location information from Wikipedia random pages. It uses
the utility `https://ca.wikipedia.org/wiki/Special:Random` which returns a
random page. 

Inspired in
[this reddit post](https://www.reddit.com/r/dataisbeautiful/comments/qu32wh/oc_map_of_50000_locations_randomly_sampled_from/).

## Usage

Current languages implemented (and somehow tested) are:

- Catalan (ca)
- Spanish (es)
- Galician (gl)
- Euskara (eu)
- Esperanto (eo)
- Italian (it)
- Deutsch (de)
- French (fr)

You would need to input the corresponding codes.

### Quick Start

```bash
pip install -r requirements.txt
./wikilocations.py -t 5000 -l ca -o locations_ca_5k.json
```

### Options

| Option               	| Meaning                                                  	| Default          	|
|----------------------	|----------------------------------------------------------	|------------------	|
| `-t` or `--target`   	| Number of locations to sample                            	| 10               	|
| `-l` or `--language` 	| Which Wikipedia to sample from (not all are implemented) 	| `ca`             	|
| `-o` or `--output`   	| File where to store the sampled locations (in json)      	| `locations.json` 	|
| `--verbise`          	| If verbose output should be given                        	| False            	|
