"""
CSV parsing service for batch processing product imports.
"""

import csv
from io import StringIO
from typing import List, Tuple, Dict


class CSVParseError(Exception):
    """Custom exception for CSV parsing errors."""
    pass


class CSVParser:
    """Parse and validate CSV files for product imports."""
    
    REQUIRED_COLUMNS = ["sku", "name"]
    OPTIONAL_COLUMNS = ["description", "price", "quantity", "active"]
    
    @staticmethod
    def parse_csv(
        file_path: str,
        batch_size: int = 10000,
    ) -> Tuple[List[Dict], List[str]]:
        """
        Parse CSV file and yield batches of product data.
        
        Args:
            file_path: Path to the CSV file
            batch_size: Number of rows per batch
            
        Yields:
            (batch of product dicts, list of error messages)
        """
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                if not reader.fieldnames:
                    raise CSVParseError("CSV file is empty")
                
                # Validate headers
                csv_columns = set(reader.fieldnames)
                required = set(CSVParser.REQUIRED_COLUMNS)
                
                if not required.issubset(csv_columns):
                    missing = required - csv_columns
                    raise CSVParseError(f"Missing required columns: {missing}")
                
                batch = []
                errors = []
                
                for row_num, row in enumerate(reader, start=2):  # Start at 2 (after header)
                    try:
                        product = CSVParser._validate_row(row)
                        batch.append(product)
                        
                        if len(batch) >= batch_size:
                            yield batch, errors
                            batch = []
                            errors = []
                    
                    except CSVParseError as e:
                        errors.append(f"Row {row_num}: {str(e)}")
                
                # Yield remaining rows
                if batch:
                    yield batch, errors
        
        except IOError as e:
            raise CSVParseError(f"Failed to read file: {str(e)}")
    
    @staticmethod
    def _validate_row(row: Dict) -> Dict:
        """
        Validate and transform a single CSV row.
        
        Args:
            row: Dictionary of CSV row data
            
        Returns:
            Validated and transformed product dictionary
            
        Raises:
            CSVParseError: If row validation fails
        """
        
        # SKU is required and must be non-empty
        sku = row.get('sku', '').strip()
        if not sku:
            raise CSVParseError("SKU is required and cannot be empty")
        
        # Name is required and must be non-empty
        name = row.get('name', '').strip()
        if not name:
            raise CSVParseError("Name is required and cannot be empty")
        
        # Parse optional fields
        product = {
            'sku': sku,
            'name': name,
        }
        
        # Description (optional)
        if 'description' in row:
            desc = row.get('description', '').strip()
            if desc:
                product['description'] = desc
        
        # Price (optional, must be numeric if provided)
        if 'price' in row:
            price_str = row.get('price', '').strip()
            if price_str:
                try:
                    product['price'] = float(price_str)
                except ValueError:
                    raise CSVParseError(f"Invalid price value: {price_str}")
        
        # Quantity (optional, must be integer if provided)
        if 'quantity' in row:
            qty_str = row.get('quantity', '').strip()
            if qty_str:
                try:
                    product['quantity'] = int(qty_str)
                except ValueError:
                    raise CSVParseError(f"Invalid quantity value: {qty_str}")
        
        # Active (optional, boolean)
        if 'active' in row:
            active_str = row.get('active', '').strip().lower()
            if active_str:
                product['active'] = active_str in ('true', '1', 'yes', 'y')
        
        return product
