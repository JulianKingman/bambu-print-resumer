# bambu-print-resumer
Has your print failed? Do you wish you could resume it where it left off? Perhaps you've watched the [CNC Kitchen Video](https://www.youtube.com/watch?v=-wjE8eDiKWg) and still can't figure it out. Fear not, that's what this little tool is for.

# How it works
1. You must have python set up
2. Export your Gcode from bambu studio
3. Run the python script:
```bash
python ResumeBambuGcode.py
```
4. Follow the prompts (you'll need to measure the height of your print in millimeters)
5. It will output a new GCODE file
6. It's worthwhile opening the GCODE file in bambu studio to make sure it looks correct before printing
7. Save the new GCODE file to your micro SD card, put it directly into the bambu printer, and print!

# Home Z-Axis (Beta)
If the z-height isn't correctly calibrated, the printer might start printing above the print or knock the print of the bed. This option alows you to home the Z axis at a custom XY position on the bed hopefully avoiding the print. Minimal testing has done on this feature.
