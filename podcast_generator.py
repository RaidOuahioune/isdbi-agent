import json
import requests
from pathlib import Path
import os
from typing import Dict, List
import markdown2
import re

class PodcastGenerator:
    """Generate podcast from enhancement results using text-to-speech APIs"""
    
    def __init__(self, api_key: str = None):
        self.eleven_labs_key = api_key or os.getenv("ELEVEN_LABS_API_KEY")
        # Default voices from ElevenLabs
        self.voices = {
            "narrator": "21m00Tcm4TlvDq8ikWAM",  # Rachel - Professional narrator
            "shariah_expert": "AZnzlk1XvdvUeBnXmlld",  # Antoine - Authoritative
            "finance_expert": "EXAVITQu4vr4xnSDxMaL",  # Bella - Professional female
            "standards_expert": "VR6AewLTigWG4xSOukaG"  # Jack - Formal male
        }
        
    def generate_podcast_script(self, md_file: str) -> List[Dict]:
        """Convert markdown enhancement results to podcast script segments"""
        
        with open(md_file, 'r') as f:
            content = f.read()
            
        # Convert markdown to HTML then strip tags for clean text
        html = markdown2.markdown(content)
        text = re.sub('<[^<]+?>', '', html)
        
        segments = []
        
        # Intro
        segments.append({
            "voice": "narrator",
            "text": "Welcome to the AAOIFI Standards Enhancement Podcast. Today we'll discuss proposed changes to FAS 10 regarding Istisna'a contracts for intangible assets."
        })
        
        # Trigger scenario
        scenario_match = re.search(r"Trigger Scenario\n\n(.*?)\n\n", text, re.DOTALL)
        if scenario_match:
            segments.append({
                "voice": "narrator",
                "text": f"The trigger scenario we're addressing is: {scenario_match.group(1)}"
            })
            
        # Expert discussions
        for expert in ["Shariah Expert", "Finance Expert", "Standards Expert"]:
            expert_match = re.search(f"{expert}\n\n.*?Analysis:(.*?)Concerns:", text, re.DOTALL)
            if expert_match:
                voice_key = expert.lower().replace(" ", "_")
                segments.append({
                    "voice": voice_key,
                    "text": f"As the {expert}, here's my analysis: {expert_match.group(1)}"
                })
                
        # Conclusion
        if "APPROVED" in text:
            segments.append({
                "voice": "narrator",
                "text": "The enhancement proposal has been approved. This represents a significant step forward in adapting Islamic finance standards for modern technological developments."
            })
            
        return segments
    
    def generate_audio_segment(self, text: str, voice_id: str) -> bytes:
        """Generate audio for a single segment using ElevenLabs API"""
        
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.eleven_labs_key
        }
        
        data = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.75,
                "similarity_boost": 0.75
            }
        }
        
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code == 200:
            return response.content
        else:
            raise Exception(f"Error generating audio: {response.status_code}")
    
    def create_podcast(self, md_file: str, output_file: str = "enhancement_podcast.mp3"):
        """Create full podcast from markdown file"""
        
        # Generate script segments
        segments = self.generate_podcast_script(md_file)
        
        # Create output directory
        Path("podcast_output").mkdir(exist_ok=True)
        
        # Generate and save individual segments
        audio_segments = []
        for i, segment in enumerate(segments):
            try:
                audio = self.generate_audio_segment(
                    segment["text"],
                    self.voices[segment["voice"]]
                )
                segment_file = f"podcast_output/segment_{i}.mp3"
                with open(segment_file, "wb") as f:
                    f.write(audio)
                audio_segments.append(segment_file)
            except Exception as e:
                print(f"Error generating segment {i}: {str(e)}")
                
        # Combine segments using pydub
        try:
            from pydub import AudioSegment
            
            combined = AudioSegment.empty()
            for segment_file in audio_segments:
                segment_audio = AudioSegment.from_mp3(segment_file)
                combined += segment_audio
                
            # Add small pause between segments
            combined = combined.append(AudioSegment.silent(duration=500), crossfade=100)
            
            # Export final podcast
            combined.export(f"podcast_output/{output_file}", format="mp3")
            
            # Cleanup segment files
            for segment_file in audio_segments:
                os.remove(segment_file)
                
            print(f"Podcast generated successfully: podcast_output/{output_file}")
            
        except Exception as e:
            print(f"Error combining audio segments: {str(e)}")

generator = PodcastGenerator(api_key="sk_ebc9b70b7d7ee7cee2a0e21ea9c0694cbbd1b81d170f1680")
generator.create_podcast("enhancement_results/enhancement_FAS10_20250516_192918.md")