import random

class DataLoader:

    def load_well_log_data():
        well_bore_name = "05-1-HT-1X"
        file_name = "1X-RWD.las"
        start_depth = "0"
        stop_depth = "5000"
        log_run = "Run#1"
        log_type = "Raw/Interpreted"
        date = "22/12/2024"
        logging_service = "Schlumberger/Halibuton"
        fluid_type = "Oil Based/ Water"
        log_class = "Petrophysics/Formation/Mudlog"
        logging_mode = "LWD/MWD/Wireline"
        
        data = [
            [well_bore_name, file_name, start_depth, str(random.randint(0, 5000)), log_run, log_type, date, logging_service, fluid_type, log_class, logging_mode]
            for _ in range(70)
        ]

        return data

    def load_marker_data():
        data = [
            ["Well A", "Top Sand", str(random.randint(0, 5000)), "High", "Geologist"]
            for _ in range(70)
        ]
        return data

    def load_well_path_data():
        data = [
            ["Well A", "1000", "5.2°", "180°"],
            ["Well B", "1500", "3.1°", "190°"],
        ] * 60
        return data

    def load_seismic_2d_data():
        data = [
            ["Survey X", "Line 101", "500", "Completed"],
            ["Survey Y", "Line 202", "750", "Pending"],
        ] * 60
        return data

    def load_seismic_3d_data():
        data = [
            ["Survey X", "Vol_001", "300", "400", "Processing"],
            ["Survey Y", "Vol_002", "350", "450", "Completed"],
        ] * 60
        return data

    def load_seismic_location_data():
        data = [
            ["Seismic A", "10.5", "106.8"],
            ["Seismic B", "11.2", "107.3"],
        ] * 60
        return data

    def load_document_data():
        data = [
            ["Well Report", "PDF", "2024-01-15", "John Doe"],
            ["Seismic Interpretation", "DOCX", "2023-12-10", "Jane Smith"],
        ] * 60
        return data