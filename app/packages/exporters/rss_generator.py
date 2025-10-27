"""RSS Generator - Creates podcast RSS feed from episodes"""
import json, sys
from pathlib import Path
from datetime import datetime
import xml.etree.ElementTree as ET

def generate_rss(job_dir: str):
    job_path = Path(job_dir)
    feed = ET.Element('rss', version='2.0')
    channel = ET.SubElement(feed, 'channel')
    ET.SubElement(channel, 'title').text = 'Alexandria Podcast'
    ET.SubElement(channel, 'description').text = 'AI-generated podcasts from knowledge sources'
    ET.SubElement(channel, 'language').text = 'en'
    
    # Add episode
    item = ET.SubElement(channel, 'item')
    ET.SubElement(item, 'title').text = f'Episode: {job_path.name}'
    ET.SubElement(item, 'guid').text = job_path.name
    ET.SubElement(item, 'pubDate').text = datetime.now().strftime('%a, %d %b %Y %H:%M:%S +0000')
    
    # Save RSS
    tree = ET.ElementTree(feed)
    output_path = Path('dist/export') / job_path.name / 'feed.xml'
    output_path.parent.mkdir(parents=True, exist_ok=True)
    tree.write(output_path, encoding='utf-8', xml_declaration=True)
    print(f'RSS feed generated: {output_path}')
    return str(output_path)

if __name__ == '__main__':
    generate_rss(sys.argv[1] if len(sys.argv) > 1 else 'tmp/test_job')
