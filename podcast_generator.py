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
        
        # Extract FAS standard number from the content
        standard_match = re.search(r"Standards Enhancement Results for FAS (\d+)", text)
        standard_id = standard_match.group(1) if standard_match else "10"
        
        # Intro
        intro_text = f"Welcome to the AAOIFI Standards Enhancement Podcast. Today we'll discuss proposed changes to FAS {standard_id}"
        
        # Try to extract more specific information about the enhancement
        enhancement_topic_match = re.search(r"regarding (.+?)(?:\.|$)", text[:500])
        if enhancement_topic_match:
            intro_text += f" regarding {enhancement_topic_match.group(1)}."
        else:
            intro_text += "."
            
        segments.append({
            "voice": "narrator",
            "text": intro_text
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
            # Try different patterns to extract expert analysis
            expert_match = None
            
            # Pattern 1: Look for Analysis: followed by Concerns:
            pattern1 = re.search(f"{expert}.*?Analysis:(.*?)Concerns:", text, re.DOTALL)
            if pattern1:
                expert_match = pattern1
                analysis_text = pattern1.group(1).strip()
                
                # Also extract concerns if available
                concerns_match = re.search(f"Concerns:(.*?)Recommendations:", text, re.DOTALL)
                if concerns_match:
                    concerns_text = concerns_match.group(1).strip()
                    analysis_text += f". My concerns include: {concerns_text}"
                
                # Extract recommendations if available
                recommendations_match = re.search(f"Recommendations:(.*?)(?:\n\n|$)", text, re.DOTALL)
                if recommendations_match:
                    recommendations_text = recommendations_match.group(1).strip()
                    analysis_text += f". I recommend: {recommendations_text}"
            
            # Pattern 2: Look for sections that might contain expert name
            if not expert_match:
                expert_section_match = re.search(f"## {expert}.*?\n(.*?)(?:\n##|\Z)", text, re.DOTALL)
                if expert_section_match:
                    analysis_text = expert_section_match.group(1).strip()
            
            # Pattern 3: Look for accumulated expert concerns/recommendations
            if not expert_match:
                expert_name_simple = expert.split()[0].lower()  # e.g., "shariah" from "Shariah Expert"
                concerns_pattern = re.search(f"{expert_name_simple}.*?concerns:(.*?)(?:\n\n|$)", text, flags=re.DOTALL|re.IGNORECASE)
                if concerns_pattern:
                    analysis_text = f"I have concerns about: {concerns_pattern.group(1).strip()}"
            
            # If we found any match, create the segment
            if expert_match or expert_section_match or concerns_pattern:
                voice_key = expert.lower().replace(" ", "_")
                segments.append({
                    "voice": voice_key,
                    "text": f"As the {expert}, here's my analysis: {analysis_text}"
                })
                
        # Try to extract recommendations if they exist separately
        recommendations_section = re.search(r"## Recommendations\s*(.*?)(?:\n##|\Z)", text, re.DOTALL)
        if recommendations_section:
            segments.append({
                "voice": "standards_expert",  # Use standards expert for general recommendations
                "text": f"Here are our recommendations: {recommendations_section.group(1).strip()}"
            })
        
        # Conclusion
        if "APPROVED" in text:
            segments.append({
                "voice": "narrator",
                "text": "The enhancement proposal has been approved. This represents a significant step forward in adapting Islamic finance standards for modern technological developments."
            })
        elif "REJECTED" in text:
            segments.append({
                "voice": "narrator",
                "text": "The enhancement proposal has been rejected. The committee has determined that further work is needed before these changes can be implemented."
            })
        elif "NEEDS REVISION" in text:
            segments.append({
                "voice": "narrator",
                "text": "The enhancement proposal needs revision. The committee has provided feedback for improvements that should be addressed in a future proposal."
            })
        else:
            segments.append({
                "voice": "narrator",
                "text": "Thank you for listening to this AAOIFI Standards Enhancement Podcast. This concludes our discussion on the proposed changes."
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

# Remove the automatic execution at module import
generator = PodcastGenerator()
# generator.create_podcast("enhancement_results/enhancement_FAS10_20250516_192918.md")