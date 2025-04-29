# pmaps
Free Projection mapping software, distorts live stream/video onto a projected surface

## Commands
`pmap`: Runs PMap, if no config is provided, an initialization will be peformed allowing for a display, and points to be chosen. Once you're happy with it, these can be saved to a config file, which can be loaded with `pmap -c /path/to/my/config.txt`.

`pmap-gui`: Runs PMap in gui mode. Is functionally identical to `pmap` with no config arguments.

`pmap-inter`: Runs PMap in an interactive terminal. Will still use some GUI elements when necessary (ex. selecting screen points, but will allow selection through the terminal)

`pmapd`: Runs PMap as a background process, requires a config file (`pmapd -c /path/to/my/config.txt`).
