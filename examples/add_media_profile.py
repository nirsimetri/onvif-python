"""
Path: examples/add_media_profile.py
Author: @kaburagisec
Created: October 30, 2025
Tested devices: EZVIZ H8C (https://www.ezviz.com/inter/product/h8c/43162)

This script connects to an ONVIF-compliant device and creates
a new media profile with video encoder configuration using the Media service.

Steps:
1. Connect to ONVIF device
2. Get available video sources
3. Get available video encoder configurations
4. Create a new media profile
5. Add video source configuration to the profile
6. Add video encoder configuration to the profile
7. Verify the profile was created successfully
"""

from onvif import ONVIFClient

HOST = "192.168.1.3"
PORT = 80
USERNAME = "admin"
PASSWORD = "admin123"

try:
    # Initialize ONVIF client
    client = ONVIFClient(HOST, PORT, USERNAME, PASSWORD)
    media = client.media()

    # Get available video sources
    print("Getting video sources...")
    video_sources = media.GetVideoSources()
    if not video_sources:
        print("No video sources available")
        exit(1)

    print(f"Found {len(video_sources)} video source(s)")
    video_source_token = video_sources[0].token
    print(f"Using video source token: {video_source_token}")

    # Get available video source configurations
    print("\nGetting video source configurations...")
    video_source_configs = media.GetVideoSourceConfigurations()
    if not video_source_configs:
        print("No video source configurations available")
        exit(1)

    video_source_config_token = video_source_configs[0].token
    print(f"Using video source configuration token: {video_source_config_token}")

    # Get available video encoder configurations
    print("\nGetting video encoder configurations...")
    video_encoder_configs = media.GetVideoEncoderConfigurations()
    if not video_encoder_configs:
        print("No video encoder configurations available")
        exit(1)

    video_encoder_config_token = video_encoder_configs[0].token
    print(f"Using video encoder configuration token: {video_encoder_config_token}")

    # Create a new media profile
    profile_name = "CustomProfile_001"
    print(f"\nCreating new media profile: {profile_name}")
    new_profile = media.CreateProfile(Name=profile_name)
    profile_token = new_profile.token
    print(f"Profile created with token: {profile_token}")

    # Add video source configuration to the profile
    print("\nAdding video source configuration to profile...")
    media.AddVideoSourceConfiguration(
        ProfileToken=profile_token, ConfigurationToken=video_source_config_token
    )
    print("Video source configuration added successfully")

    # Add video encoder configuration to the profile
    print("\nAdding video encoder configuration to profile...")
    media.AddVideoEncoderConfiguration(
        ProfileToken=profile_token, ConfigurationToken=video_encoder_config_token
    )
    print("Video encoder configuration added successfully")

    # Verify the profile was created
    print("\nVerifying profile creation...")
    profile = media.GetProfile(ProfileToken=profile_token)
    print(f"\nProfile Details:")
    print(f"  Name: {profile.Name}")
    print(f"  Token: {profile.token}")
    if (
        hasattr(profile, "VideoSourceConfiguration")
        and profile.VideoSourceConfiguration
    ):
        print(
            f"  Video Source: {profile.VideoSourceConfiguration.SourceToken if hasattr(profile.VideoSourceConfiguration, 'SourceToken') else 'N/A'}"
        )
    if (
        hasattr(profile, "VideoEncoderConfiguration")
        and profile.VideoEncoderConfiguration
    ):
        print(
            f"  Video Encoder: {profile.VideoEncoderConfiguration.Encoding if hasattr(profile.VideoEncoderConfiguration, 'Encoding') else 'N/A'}"
        )

    print("\n✓ Media profile created and configured successfully!")

    # Optional: Get stream URI for the new profile
    print("\nGetting stream URI for the new profile...")
    stream_setup = {"Stream": "RTP-Unicast", "Transport": {"Protocol": "RTSP"}}
    stream_uri = media.GetStreamUri(
        StreamSetup=stream_setup, ProfileToken=profile_token
    )
    print(f"Stream URI: {stream_uri.Uri}")

except Exception as e:
    print(f"Error: {e}")
    import traceback

    traceback.print_exc()
