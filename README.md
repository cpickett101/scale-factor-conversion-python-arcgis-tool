# GIS CAD Scale Factor Tool

An ArcGIS Python Toolbox for converting between GIS grid coordinates and CAD/real-world surface measurements while preserving true curve geometry.

![Python Version](https://img.shields.io/badge/python-3.x-blue.svg)
![ArcGIS Pro](https://img.shields.io/badge/ArcGIS%20Pro-3.x-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## Screenshots

![Tool Interface](images/tool-interface.png)

*The Scale Factor tool interface in ArcGIS Pro*

### Point Conversion
![Point Conversion Demo](images/Demo_point.gif)
*Scaling point features while preserving coordinates*

### Line Conversion
![Line Conversion Demo](images/demo_line.gif)
*Scaling polyline features with curve preservation*

### Polygon Conversion
![Polygon Conversion Demo](images/Demo_polygon.gif)
*Scaling polygon features maintaining boundary integrity*

## Overview

This tool applies scale factors to GIS feature classes, commonly needed when converting between State Plane coordinate systems and ground/surface measurements used in CAD systems. The tool intelligently preserves circular arcs and bezier curves from CAD imports instead of converting them to straight line segments.

**Important:** This tool is designed for features in State Plane coordinate systems. The input feature class must have a State Plane projection defined before running the tool.

## Features

- **Bidirectional Conversion**: Convert from Grid to Surface (GIS → CAD) or Surface to Grid (CAD → GIS)
- **Curve Preservation**: Maintains true circular arcs and bezier curves from CAD geometry
- **Multiple Geometry Types**: Supports Points, Polylines, and Polygons
- **Smart Validation**: Automatic validation of scale factors based on conversion direction
- **Progress Tracking**: Real-time progress updates during processing

## Requirements

- **ArcGIS Pro 3.x** or later
- **Python 3.x** (included with ArcGIS Pro)
- **Advanced ArcGIS license** (for certain geometry operations)
- **Input data must be in a State Plane coordinate system**

## Installation

### Clone the Repository

```bash
git clone https://github.com/yourusername/gis-cad-scale-factor.git
```

### Add to ArcGIS Pro

1. Open ArcGIS Pro
2. In the Catalog pane, right-click on **Toolboxes**
3. Select **Add Toolbox**
4. Navigate to the downloaded `ScaleFactor.pyt` file
5. Click **OK**

## Pre-Processing: Ensure State Plane Projection

**Critical Step:** Before using this tool, verify your input features are in a State Plane coordinate system.

### Check Current Projection

1. Right-click on your feature class in the Catalog pane
2. Select **Properties**
3. Click the **Spatial Reference** tab
4. Verify the coordinate system is a State Plane system (e.g., "NAD 1983 State Plane Texas Central FIPS 4203")

### Project to State Plane (if needed)

If your data is in a different coordinate system:

1. Open the **Project** tool (Data Management Tools → Projections and Transformations → Feature → Project)
2. Set **Input Dataset or Feature Class**: Your feature class
3. Set **Output Dataset or Feature Class**: Name for the projected output
4. Click the **Output Coordinate System** browse button
5. Navigate to: **Projected Coordinate Systems → State Plane**
6. Select the appropriate State Plane zone for your area
7. Choose the correct datum (NAD 1983 is most common)
8. Click **OK** and run the tool

### Selecting the Correct State Plane Zone

Choose the State Plane zone that covers your project area. Common zones include:

- **Texas Central (FIPS 4203)**: Central Texas including Austin area
- **Texas North Central (FIPS 4202)**: Dallas-Fort Worth area
- **Texas South Central (FIPS 4204)**: San Antonio area
- **California Zone 5 (FIPS 0405)**: Los Angeles area
- **Florida East (FIPS 0901)**: Miami area

Consult with your project surveyor or geodetic control documentation for the appropriate zone.

## Usage

### Basic Workflow

1. **Verify State Plane projection** (see Pre-Processing section above)

2. **Open the tool** from the Catalog pane under Toolboxes

3. **Set parameters**:
   - **Input Features**: Select the feature class to scale (must be in State Plane)
   - **Output Features**: Specify the output location
   - **Conversion Direction**: Choose Grid to Surface or Surface to Grid
   - **Scale Factor**: Enter the appropriate scale factor

4. **Run the tool**

### Scale Factor Guidelines

#### Grid to Surface (GIS → CAD)

- Use scale factors **greater than 1.0**
- Example: 1.00012 for Texas Central State Plane
- Converts from State Plane grid coordinates to ground/surface measurements

#### Surface to Grid (CAD → GIS)

- Use scale factors **less than 1.0**
- Example: 0.99988 for Texas Central State Plane
- Converts from ground/surface measurements to State Plane grid coordinates

### Determining Your Scale Factor

Scale factors are location-specific and depend on:
- The State Plane zone
- Your project's location within that zone
- Elevation above the reference ellipsoid

**To find your project's scale factor:**
1. Consult your project's surveying control documentation
2. Use geodetic software to calculate the combined scale factor for your location
3. Contact your project surveyor or geodetic control provider
4. Reference NOAA's State Plane Coordinate System tools

### Common Scale Factors by State Plane Zone

| State Plane Zone | Grid to Surface | Surface to Grid |
|------------------|-----------------|-----------------|
| Texas Central    | 1.00012         | 0.99988         |
| Texas North      | 1.00008         | 0.99992         |
| Texas South      | 1.00016         | 0.99984         |

*Note: These are approximate values. Scale factors vary by location within each zone. Always consult your project's geodetic control for exact values.*

## Example

Converting CAD surface measurements to State Plane grid coordinates:

```
Input: CAD_Import.shp (with curved features, already in State Plane)
Output: Grid_Coordinates.shp
Direction: Surface to Grid (CAD → GIS, factor < 1.0)
Scale Factor: 0.99988
```

**Result:** All features scaled by 0.99988, with curved geometry preserved.

## Technical Details

### Curve Preservation

The tool uses ArcGIS's JSON geometry representation to detect and preserve true curves:
- Circular arcs from CAD are maintained as circular arcs
- Bezier curves are preserved
- All coordinate values are scaled while maintaining curve definitions
- Straight line segments are processed using traditional vertex-by-vertex scaling

### Supported Geometry Types

- **Points**: X and Y coordinates scaled, Z values preserved
- **Polylines**: All vertices and curves scaled proportionally
- **Polygons**: All rings scaled, closure automatically maintained

## Troubleshooting

### "Scale factor must be greater/less than 1.0" Error

- Check that your scale factor matches the conversion direction
- Grid to Surface requires factors > 1.0
- Surface to Grid requires factors < 1.0

### Incorrect Output Coordinates

- Verify your input features are in a State Plane coordinate system
- Check that you're using the correct scale factor for your project location
- Ensure you've selected the correct conversion direction

### Curves Not Preserved

- Ensure input data is stored in a File Geodatabase (not shapefile)
- Shapefiles don't support true curve geometry
- Use Feature Class to Feature Class tool to convert to FGDB if needed

### Output Features Not Appearing

- Check that the output path is valid
- Ensure you have write permissions to the output location
- Verify the output workspace exists

### Wrong State Plane Zone

- If results seem incorrect, verify you've selected the appropriate State Plane zone
- Consult with your surveyor to confirm the correct zone for your project area
- Use the Project tool to reproject to the correct State Plane zone

## References

### State Plane Coordinate System Resources

- **NOAA's State Plane Coordinate System Information**: [https://geodesy.noaa.gov/SPCS/](https://geodesy.noaa.gov/SPCS/)
- **EPSG Geodetic Parameter Dataset**: [https://epsg.org/](https://epsg.org/)
- **ArcGIS Pro Coordinate System Documentation**: [Esri Support - Coordinate Systems](https://pro.arcgis.com/en/pro-app/latest/help/mapping/properties/coordinate-systems-and-projections.htm)

### Scale Factor Calculation

- **NGS Geodetic Toolkit**: [https://geodesy.noaa.gov/TOOLS/](https://geodesy.noaa.gov/TOOLS/)
- **State Plane Coordinate System Parameters**: Available from state geodetic control offices
- **Professional Surveying Guidance**: Consult with a licensed surveyor for project-specific requirements

### Related Standards

- **FGDC Geospatial Positioning Accuracy Standards**: For understanding coordinate system accuracy requirements
- **State and Local Geodetic Control**: Contact your state's department of transportation or surveying board

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Developed for GIS and CAD integration workflows
- Thanks to the ArcGIS Python community for geometry handling best practices
- Special thanks to surveying and geodetic professionals who contributed to understanding scale factor applications

## Author

- GitHub: [@cpickett101](https://github.com/cpickett101)
- Email: christopherbpickett@gmail.com
- LinkedIn: [Christopher Pickett](https://www.linkedin.com/in/christopher-p-a4908979/)

## Support

If you encounter any issues or have questions:
- Open an [issue](https://github.com/cpickett101/gis-cad-scale-factor/issues)
- Check existing issues for solutions
- Submit a pull request

## Version History

- **1.0.0** (2025-10-20)
  - Initial release
  - Support for curve preservation
  - Bidirectional conversion support
  - Automatic scale factor validation

---

**Important Notes:** 
- This tool requires input features to be in a State Plane coordinate system
- This tool requires a File Geodatabase for full curve geometry support
- Shapefiles do not support true curves and will convert them to line segments
- Always verify your projection and scale factor before processing
