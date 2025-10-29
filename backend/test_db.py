#!/usr/bin/env python3
"""
Test script to check database operations for template saving
"""
import sqlite3
import os
import json

def check_database():
    db_path = 'certificates.db'
    
    print(f"Database file exists: {os.path.exists(db_path)}")
    print(f"Database file size: {os.path.getsize(db_path) if os.path.exists(db_path) else 0} bytes")
    
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        # Check table structure
        c.execute("PRAGMA table_info(templates)")
        columns = c.fetchall()
        print("\nTemplates table structure:")
        for col in columns:
            print(f"  {col[1]} ({col[2]})")
        
        # Count templates
        c.execute("SELECT COUNT(*) FROM templates")
        count = c.fetchone()[0]
        print(f"\nNumber of templates: {count}")
        
        # List all templates
        c.execute("SELECT id, name, language, created_at FROM templates")
        templates = c.fetchall()
        print("\nExisting templates:")
        for template in templates:
            print(f"  ID: {template[0]}, Name: {template[1]}, Language: {template[2]}, Created: {template[3]}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"Database error: {e}")
        return False

def test_template_creation():
    """Test creating a template directly in database"""
    try:
        conn = sqlite3.connect('certificates.db')
        c = conn.cursor()
        
        # Test data
        test_template = {
            'name': 'Test Urdu Template',
            'image_base64': 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==',
            'text_x': 100.0,
            'text_y': 200.0,
            'font': 'NotoNastaliqUrdu-Regular.ttf',
            'font_size': 24,
            'alignment': 'center',
            'color': '#000000',
            'language': 'ur'
        }
        
        c.execute('''
            INSERT INTO templates (name, image_base64, text_x, text_y, font, font_size, alignment, color, language)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            test_template['name'],
            test_template['image_base64'],
            test_template['text_x'],
            test_template['text_y'],
            test_template['font'],
            test_template['font_size'],
            test_template['alignment'],
            test_template['color'],
            test_template['language']
        ))
        
        template_id = c.lastrowid
        conn.commit()
        conn.close()
        
        print(f"\nSuccessfully created test template with ID: {template_id}")
        return template_id
        
    except Exception as e:
        print(f"\nFailed to create test template: {e}")
        return None

if __name__ == "__main__":
    print("=== Database Check ===")
    check_database()
    
    print("\n=== Test Template Creation ===")
    test_template_creation()
    
    print("\n=== Database Check After Creation ===")
    check_database()