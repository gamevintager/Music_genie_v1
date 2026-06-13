from ollama import chat

def get_intent(prompt):

    response = chat(
        model="llama3.2",
        messages=[
            {
                "role": "system",
                "content": """
                You are an intent classifier.

                Examples:

                I'm stressed before an exam
                MOOD_STRESS

                I need to focus
                MOOD_STRESS

                I want to relax
                MOOD_RELAX

                Gym music
                MOOD_WORKOUT

                Show songs
                SHOW_SONGS

                Statistics
                SHOW_STATS

                Play a random song
                PLAY_RANDOM

                Return ONLY the intent.
                """
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                )

    return response["message"]["content"].strip()

def ask_music_genie(prompt, songs):

    song_list = "\n".join(
        [
            f"{song['title']} | Duration: {song['duration']} seconds"
            for song in songs
        ]
    )

    response = chat(
        model="llama3.2",
        messages=[
            {
                "role": "system",
                "content": f"""
                You are Music Genie.

                User library:

                {song_list}

                Only recommend songs from this library.
                Keep responses short and helpful.
                """
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response["message"]["content"]