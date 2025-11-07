import flyr
import json
import pandas as pd
import os


def extract_all_attributes(obj, description="", max_depth=3, current_depth=0):
    """Recursively extract all attributes from an object"""
    if current_depth >= max_depth:
        return str(obj)

    result = {}

    try:
        for attr in dir(obj):
            if not attr.startswith("_") and not callable(getattr(obj, attr)):
                try:
                    value = getattr(obj, attr)
                    if value is not None:
                        # Handle different types of values
                        if hasattr(value, "tolist"):
                            result[attr] = value.tolist()
                        elif isinstance(value, (str, int, float, bool)):
                            result[attr] = value
                        elif isinstance(value, (list, tuple)):
                            result[attr] = list(value)
                        elif isinstance(value, dict):
                            # Handle dictionary with potential non-serializable values
                            clean_dict = {}
                            for k, v in value.items():
                                try:
                                    json.dumps(v)
                                    clean_dict[k] = v
                                except (TypeError, ValueError):
                                    # Convert non-serializable values to string or float
                                    if hasattr(v, "__float__"):
                                        try:
                                            clean_dict[k] = float(v)
                                        except:
                                            clean_dict[k] = str(v)
                                    else:
                                        clean_dict[k] = str(v)
                            result[attr] = clean_dict
                        elif hasattr(value, "__dict__"):
                            # Recursively extract nested objects
                            result[attr] = extract_all_attributes(
                                value,
                                f"{description}.{attr}",
                                max_depth,
                                current_depth + 1,
                            )
                        else:
                            try:
                                json.dumps(value)  # Test if JSON serializable
                                result[attr] = value
                            except (TypeError, ValueError):
                                # Handle non-serializable types (like IFDRational)
                                if hasattr(value, "__float__"):
                                    try:
                                        result[attr] = float(value)
                                    except:
                                        result[attr] = str(value)
                                else:
                                    result[attr] = str(value)
                except Exception as e:
                    print(f"Warning: Could not extract {attr} from {description}: {e}")
                    continue
    except Exception as e:
        print(f"Warning: Could not iterate attributes of {description}: {e}")
        return str(obj)

    return result


file_path = r"C:\projects\tenesso\image_subtraction"
img = "FLIR0089.jpg"
img = "FLIR0139.jpg"
thermogram = flyr.unpack(os.path.join(file_path, img))

# Extract base filename for output files
base_name = os.path.splitext(img)[0]

# Initialize data structure
thermogram_data = {
    "image_filename": img,
}

# Extract all thermogram attributes automatically
print("Extracting all thermogram attributes...")
try:
    all_data = extract_all_attributes(thermogram, "thermogram")
    thermogram_data.update(all_data)

    # Special handling for celsius data - mark as saved separately
    if "celsius" in all_data and all_data["celsius"] is not None:
        thermogram_data["celsius_data_info"] = (
            "Temperature data saved to separate xlsx file"
        )
        celsius_array = all_data["celsius"]
    else:
        celsius_array = None

except Exception as e:
    print(f"Error extracting thermogram data: {e}")
    celsius_array = None

# Save thermogram data to JSON
json_filename = os.path.join(file_path, f"{base_name}_thermogram_data.json")
try:
    with open(json_filename, "w", encoding="utf-8") as json_file:
        json.dump(thermogram_data, json_file, indent=2, ensure_ascii=False)
    print(f"Thermogram data saved to: {json_filename}")
except Exception as e:
    print(f"Error saving JSON file: {e}")

# Save data to Excel with multiple sheets
xlsx_filename = os.path.join(file_path, f"{base_name}_thermogram_data.xlsx")
try:
    with pd.ExcelWriter(xlsx_filename, engine="openpyxl") as writer:

        def save_to_sheet(data, sheet_name, max_sheet_name_length=31):
            """Save data to Excel sheet with proper formatting"""
            # Truncate sheet name if too long
            if len(sheet_name) > max_sheet_name_length:
                sheet_name = sheet_name[:max_sheet_name_length]

            # Remove invalid characters from sheet name
            invalid_chars = ["\\", "/", "*", "[", "]", ":", "?"]
            for char in invalid_chars:
                sheet_name = sheet_name.replace(char, "_")

            try:
                if isinstance(data, (list, tuple)) and len(data) > 0:
                    # Handle arrays/lists
                    if isinstance(data[0], (list, tuple)):
                        # 2D array - create DataFrame directly
                        df = pd.DataFrame(data)
                        df.to_excel(writer, sheet_name=sheet_name, index=False)
                    else:
                        # 1D array - create single column DataFrame
                        df = pd.DataFrame(data, columns=[sheet_name])
                        df.to_excel(writer, sheet_name=sheet_name, index=False)

                elif isinstance(data, dict):
                    # Handle dictionaries - create DataFrame with keys as columns
                    # Create a single row DataFrame with keys as column headers
                    df = pd.DataFrame([data])
                    df.to_excel(writer, sheet_name=sheet_name, index=False)

                else:
                    # Handle simple values
                    df = pd.DataFrame([{sheet_name: str(data)}])
                    df.to_excel(writer, sheet_name=sheet_name, index=False)

                print(f"Sheet '{sheet_name}' created successfully")

            except Exception as e:
                print(f"Warning: Could not create sheet '{sheet_name}': {e}")

        # Process all extracted data
        for key, value in thermogram_data.items():
            if key == "image_filename" or key == "celsius_data_info":
                continue

            if isinstance(value, (list, tuple)) and len(value) > 0:
                # Arrays get their own sheets
                save_to_sheet(value, key)

            elif isinstance(value, dict) and len(value) > 0:
                # Dictionaries get their own sheets
                save_to_sheet(value, key)

                # For nested dictionaries, create separate sheets for each sub-dict
                for sub_key, sub_value in value.items():
                    if isinstance(sub_value, dict) and len(sub_value) > 0:
                        sheet_name = f"{key}_{sub_key}"
                        save_to_sheet(sub_value, sheet_name)

            elif isinstance(value, (str, int, float, bool)) and value is not None:
                # Simple values can be grouped in a summary sheet
                continue

        # Create a summary sheet with basic information
        summary_data = {
            "Property": [],
            "Value": [],
        }

        for key, value in thermogram_data.items():
            if isinstance(value, (str, int, float, bool)) and value is not None:
                summary_data["Property"].append(key)
                summary_data["Value"].append(str(value))

        if summary_data["Property"]:
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name="Summary", index=False)
            print("Summary sheet created successfully")

    print(f"Excel file with multiple sheets saved to: {xlsx_filename}")

except Exception as e:
    print(f"Error saving Excel file: {e}")

print("Extraction completed!")
