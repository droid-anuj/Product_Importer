"""
Product transformer utilities for data transformation.
"""

from typing import Dict, List, Optional


class ProductTransformer:
    """Transform and validate product data."""
    
    @staticmethod
    def normalize_sku(sku: str) -> str:
        """
        Normalize SKU for case-insensitive comparison.
        
        Args:
            sku: Product SKU
            
        Returns:
            Normalized SKU
        """
        return sku.strip().upper()
    
    @staticmethod
    def sanitize_string(value: str) -> str:
        """
        Sanitize string values.
        
        Args:
            value: String value
            
        Returns:
            Sanitized string
        """
        if not value:
            return None
        return value.strip()
    
    @staticmethod
    def parse_boolean(value: str) -> bool:
        """
        Parse boolean values from string.
        
        Args:
            value: String value
            
        Returns:
            Boolean value
        """
        if not value:
            return True  # Default to True
        return value.strip().lower() in ('true', '1', 'yes', 'y')
    
    @staticmethod
    def transform_product(row: Dict) -> Dict:
        """
        Transform raw product data.
        
        Args:
            row: Raw product dictionary
            
        Returns:
            Transformed product dictionary
        """
        
        transformed = {
            'sku': ProductTransformer.normalize_sku(row.get('sku', '')),
            'name': ProductTransformer.sanitize_string(row.get('name', '')),
        }
        
        # Optional fields
        if 'description' in row:
            desc = ProductTransformer.sanitize_string(row.get('description'))
            if desc:
                transformed['description'] = desc
        
        if 'price' in row and row.get('price'):
            try:
                transformed['price'] = float(row.get('price'))
            except (ValueError, TypeError):
                pass
        
        if 'quantity' in row and row.get('quantity'):
            try:
                transformed['quantity'] = int(row.get('quantity'))
            except (ValueError, TypeError):
                pass
        
        if 'active' in row:
            transformed['active'] = ProductTransformer.parse_boolean(row.get('active', 'true'))
        
        return transformed
