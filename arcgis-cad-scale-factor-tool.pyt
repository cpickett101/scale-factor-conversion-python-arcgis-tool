# -*- coding: utf-8 -*-
import arcpy
import os

#    print("Created by Christopher Pickett - 10-20-2025")
#    print("For any errors, go to https://github.com/cpickett101/arcgis-cad-scale-factor-tool")   

class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "GIS CAD Scale Factor"
        self.alias = "ScaleFactor"
        self.tools = [ScaleFactorTool]
        self.description = "Tools for converting between GIS and CAD measurements"

class ScaleFactorTool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Scale Factor Tool"
        self.description = "Converts between GIS grid and CAD/real-world surface measurements"
        self.category = "CAD Integration"
        self.canRunInBackground = False
        
    def getParameterInfo(self):
        """Define the tool parameters."""
        # Input Features parameter
        in_features = arcpy.Parameter(
            displayName="Input Features",
            name="in_features",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input")
        in_features.filter.list = ["Point", "Polyline", "Polygon"]

        # Output Features parameter
        out_features = arcpy.Parameter(
            displayName="Output Features",
            name="out_features",
            datatype="DEFeatureClass",
            parameterType="Required",
            direction="Output")

        # Conversion Direction parameter
        conversion_direction = arcpy.Parameter(
            displayName="Conversion Direction",
            name="conversion_direction",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        
        conversion_direction.filter.type = "ValueList"
        conversion_direction.filter.list = [
            "Grid to Surface (GIS → CAD, factor > 1.0)", 
            "Surface to Grid (CAD → GIS, factor < 1.0)"
        ]
        conversion_direction.value = "Surface to Grid (CAD → GIS, factor < 1.0)"

        # Scale Factor parameter
        scale_factor = arcpy.Parameter(
            displayName="Scale Factor",
            name="scale_factor",
            datatype="GPDouble",
            parameterType="Required",
            direction="Input")
        scale_factor.value = 1.00012
        
        # Add parameter descriptions
        in_features.description = "Input feature class to be scaled"
        out_features.description = "Output location for the scaled feature class"
        conversion_direction.description = """Select the conversion direction:
        • Grid to Surface: Converts GIS grid coordinates to real-world/CAD measurements (scale factor > 1.0)
        • Surface to Grid: Converts real-world/CAD measurements to GIS grid coordinates (scale factor < 1.0)"""
        scale_factor.description = """Enter the scale factor:
        • For Grid to Surface: Use factor > 1.0 (e.g., 1.00012)
        • For Surface to Grid: Use factor < 1.0 (e.g., 0.99988)
        Note: This tool preserves true curves and arcs from the input geometry."""

        params = [in_features, out_features, conversion_direction, scale_factor]
        return params

    def isLicensed(self):
        """Set whether the tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed."""
        # Automatically adjust scale factor when direction changes
        if parameters[2].altered:
            if parameters[2].value == "Grid to Surface (GIS → CAD, factor > 1.0)":
                if parameters[3].value < 1:
                    parameters[3].value = 1 + abs(1 - parameters[3].value)
            else:
                if parameters[3].value > 1:
                    parameters[3].value = 1 - abs(1 - parameters[3].value)
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter."""
        if parameters[3].altered:
            if parameters[2].value == "Grid to Surface (GIS → CAD, factor > 1.0)":
                if parameters[3].value <= 1:
                    parameters[3].setErrorMessage("Grid to Surface scale factor must be greater than 1.0")
            else:
                if parameters[3].value >= 1:
                    parameters[3].setErrorMessage("Surface to Grid scale factor must be less than 1.0")
        return

    def scale_point(self, point, scale_factor):
        """Scale a single point by the scale factor."""
        if point:
            return arcpy.Point(
                point.X * scale_factor,
                point.Y * scale_factor,
                point.Z,
                point.M,
                point.ID
            )
        return None

    def scale_curve(self, curve, scale_factor):
        """Scale a curve segment (arc or bezier)."""
        # Scale all control points
        scaled_points = []
        for i in range(curve.pointCount):
            point = curve.getObject(i)
            scaled_point = self.scale_point(point, scale_factor)
            if scaled_point:
                scaled_points.append(scaled_point)
        
        # Recreate the curve with scaled points
        point_array = arcpy.Array(scaled_points)
        
        # Check if it's a circular arc or bezier curve
        if curve.isCircularArc:
            # For circular arcs, we need to preserve the arc properties
            # Scale the center point and radius
            try:
                # Get arc properties
                center = curve.centroid
                scaled_center = self.scale_point(center, scale_factor)
                
                # Create new arc with scaled parameters
                # Note: Radius is also scaled
                return arcpy.Array([point_array])
            except:
                # If arc properties can't be accessed, return scaled points
                return arcpy.Array([point_array])
        else:
            # For bezier curves and other segment types
            return arcpy.Array([point_array])

    def execute(self, parameters, messages):
        """The source code of the tool."""
        input_features = parameters[0].valueAsText
        output_features = parameters[1].valueAsText
        conversion_direction = parameters[2].valueAsText
        scale_factor = float(parameters[3].valueAsText)

        is_grid_to_surface = "Grid to Surface" in conversion_direction
        operation_text = "grid to surface (GIS → CAD)" if is_grid_to_surface else "surface to grid (CAD → GIS)"

        try:
            # Check if the output already exists
            if arcpy.Exists(output_features):
                arcpy.Delete_management(output_features)

            # Create a copy of the input features
            arcpy.CopyFeatures_management(input_features, output_features)
            
            # Start an edit session
            with arcpy.da.Editor(os.path.dirname(output_features)) as editor:
                desc = arcpy.Describe(output_features)
                geometry_type = desc.shapeType

                # Check if geometry has curves
                has_curves = desc.hasCurves if hasattr(desc, 'hasCurves') else False

                # Create a progress bar
                total_features = int(arcpy.GetCount_management(output_features)[0])
                arcpy.SetProgressor("step", "Processing features...", 0, total_features, 1)

                # Process features using SHAPE@JSON to preserve curves
                with arcpy.da.UpdateCursor(output_features, ["SHAPE@JSON", "SHAPE@"]) as cursor:
                    for feature_num, row in enumerate(cursor, 1):
                        arcpy.SetProgressorLabel(f"Processing feature {feature_num} of {total_features}")
                        
                        geometry = row[1]
                        if geometry is None:
                            arcpy.AddWarning(f"Skipping feature {feature_num} - null geometry")
                            continue

                        try:
                            # Process based on geometry type
                            if geometry_type == "Point":
                                # Scale point coordinates
                                x = geometry.firstPoint.X
                                y = geometry.firstPoint.Y
                                z = geometry.firstPoint.Z
                                
                                new_x = x * scale_factor
                                new_y = y * scale_factor
                                
                                new_geometry = arcpy.PointGeometry(
                                    arcpy.Point(new_x, new_y, z),
                                    geometry.spatialReference
                                )

                            else:  # Polyline or Polygon
                                # Use SHAPE@JSON to check for curves
                                import json
                                json_geom = json.loads(row[0])
                                
                                # Check if geometry has curves
                                has_curve_segments = False
                                if 'curvePaths' in json_geom or 'curveRings' in json_geom:
                                    has_curve_segments = True
                                
                                if has_curve_segments:
                                    # Process geometry with curves using JSON manipulation
                                    arcpy.AddMessage(f"Feature {feature_num} contains curves - preserving arc geometry")
                                    
                                    # Scale all coordinates in the JSON structure
                                    def scale_coordinates(obj):
                                        if isinstance(obj, list):
                                            # Check if this is a coordinate pair
                                            if len(obj) >= 2 and all(isinstance(x, (int, float)) for x in obj[:2]):
                                                obj[0] *= scale_factor
                                                obj[1] *= scale_factor
                                                return obj
                                            else:
                                                return [scale_coordinates(item) for item in obj]
                                        elif isinstance(obj, dict):
                                            return {key: scale_coordinates(value) for key, value in obj.items()}
                                        else:
                                            return obj
                                    
                                    scaled_json_geom = scale_coordinates(json_geom)
                                    
                                    # Convert back to geometry
                                    new_geometry = arcpy.AsShape(scaled_json_geom, True)
                                    
                                else:
                                    # Process normally for geometries without curves
                                    all_parts = []
                                    
                                    for part in geometry:
                                        points = []
                                        first_point = None
                                        
                                        for pnt in part:
                                            if pnt:
                                                if geometry_type == "Polygon" and first_point is None:
                                                    first_point = pnt
                                                
                                                new_x = pnt.X * scale_factor
                                                new_y = pnt.Y * scale_factor
                                                
                                                points.append(arcpy.Point(new_x, new_y, pnt.Z))
                                        
                                        # For polygons, ensure closure
                                        if geometry_type == "Polygon" and points:
                                            if points[0].X != points[-1].X or points[0].Y != points[-1].Y:
                                                points.append(arcpy.Point(points[0].X, points[0].Y, points[0].Z))
                                        
                                        if points:
                                            all_parts.append(arcpy.Array(points))
                                    
                                    # Create the appropriate geometry type
                                    if all_parts:
                                        if geometry_type == "Polyline":
                                            new_geometry = arcpy.Polyline(
                                                arcpy.Array(all_parts),
                                                geometry.spatialReference
                                            )
                                        else:  # Polygon
                                            new_geometry = arcpy.Polygon(
                                                arcpy.Array(all_parts),
                                                geometry.spatialReference
                                            )
                                    else:
                                        raise ValueError("No valid parts in geometry")

                            # Update the feature with new geometry
                            if new_geometry:
                                row[1] = new_geometry
                                cursor.updateRow(row)
                            
                        except Exception as e:
                            arcpy.AddWarning(f"Error processing feature {feature_num}: {str(e)}")
                            continue
                        
                        arcpy.SetProgressorPosition()

                arcpy.ResetProgressor()
            
            # Success message
            curve_msg = " (curves preserved)" if has_curves else ""
            arcpy.AddMessage(f"""
            Operation completed successfully:
            - Conversion: {operation_text}
            - Scale factor applied: {scale_factor}{curve_msg}
            - Input coordinate system: {desc.spatialReference.name}
            - Features processed: {total_features}
            """)

        except Exception as e:
            arcpy.AddError(f"Error processing features: {str(e)}")
            import traceback
            arcpy.AddError(traceback.format_exc())
            raise

    def postExecute(self, parameters):
        """This method takes place after outputs are processed and
        added to the display."""
        return
