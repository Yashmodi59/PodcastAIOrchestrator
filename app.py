import streamlit as st
import os
import time
import uuid
from orchestration.workflow import PodcastWorkflow
from utils.storage import save_user_preferences, load_user_preferences, load_podcasts, save_podcast

# Page configuration
st.set_page_config(
    page_title="AI Podcast Creator",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state variables if they don't exist
if "user_id" not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())
if "preferences" not in st.session_state:
    st.session_state.preferences = load_user_preferences(st.session_state.user_id)
if "podcasts" not in st.session_state:
    st.session_state.podcasts = load_podcasts(st.session_state.user_id)
if "current_podcast" not in st.session_state:
    st.session_state.current_podcast = None
if "workflow" not in st.session_state:
    st.session_state.workflow = None
if "step" not in st.session_state:
    st.session_state.step = 0
if "show_history" not in st.session_state:
    st.session_state.show_history = False

# Sidebar for user preferences and navigation
with st.sidebar:
    st.title("🎙️ AI Podcast Creator")
    
    # User preferences
    st.subheader("Your Preferences")
    preferred_topics = st.multiselect(
        "Topics of Interest", 
        ["Technology", "Science", "Business", "Health", "Politics", "Entertainment", "Education", "Sports", "Travel", "History"],
        default=st.session_state.preferences.get("preferred_topics", [])
    )
    
    preferred_length = st.slider(
        "Preferred Podcast Length (minutes)", 
        min_value=5, 
        max_value=60, 
        value=st.session_state.preferences.get("preferred_length", 15),
        step=5
    )
    
    preferred_style = st.selectbox(
        "Preferred Style",
        ["Conversational", "Educational", "Interview", "Storytelling", "News"],
        index=["Conversational", "Educational", "Interview", "Storytelling", "News"].index(
            st.session_state.preferences.get("preferred_style", "Conversational")
        )
    )
    
    # Save preferences button
    if st.button("Save Preferences", key="save_preferences"):
        preferences = {
            "preferred_topics": preferred_topics,
            "preferred_length": preferred_length,
            "preferred_style": preferred_style
        }
        save_user_preferences(st.session_state.user_id, preferences)
        st.session_state.preferences = preferences
        st.success("Preferences saved!")
    
    # Navigation
    st.subheader("Navigation")
    if st.button("Create New Podcast", key="nav_new_podcast"):
        st.session_state.step = 0
        st.session_state.current_podcast = None
        st.session_state.workflow = None
        st.session_state.show_history = False
        # Clear topic suggestions to get fresh ones based on updated preferences
        if "topic_suggestions" in st.session_state:
            del st.session_state.topic_suggestions
    
    if st.button("View Podcast History", key="nav_history"):
        st.session_state.show_history = True
    
    # Email subscription form
    st.subheader("Subscribe for Updates")
    email = st.text_input("Email Address")
    if st.button("Subscribe", key="subscribe_button") and email:
        # Add email to subscribers list
        with open("subscribers.txt", "a") as f:
            f.write(f"{email}\n")
        st.success(f"Subscribed {email} to podcast updates!")

# Main content area
if st.session_state.show_history:
    st.title("Your Podcast History")
    
    if not st.session_state.podcasts:
        st.info("You haven't created any podcasts yet.")
    else:
        for i, podcast in enumerate(st.session_state.podcasts):
            with st.expander(f"Podcast: {podcast['title']}"):
                st.write(f"**Topic:** {podcast['topic']}")
                st.write(f"**Date Created:** {podcast['date_created']}")
                
                # Display tabs for different podcast elements
                tabs = st.tabs(["Script", "Audio", "Promotion"])
                
                with tabs[0]:
                    st.markdown(podcast['script'])
                
                with tabs[1]:
                    if podcast.get('audio_path'):
                        st.audio(podcast['audio_path'])
                    else:
                        st.warning("Audio not available for this podcast.")
                
                with tabs[2]:
                    st.subheader("Social Media Content")
                    st.write(f"**Title:** {podcast['promotion']['title']}")
                    st.write(f"**Post:** {podcast['promotion']['post']}")
                    st.write(f"**Summary:** {podcast['promotion']['summary']}")
else:
    # Podcast creation workflow
    st.title("Create Your AI Podcast")
    
    # Initialize workflow if not already done
    if st.session_state.workflow is None:
        st.session_state.workflow = PodcastWorkflow(user_id=st.session_state.user_id, preferences=st.session_state.preferences)
    
    # Step 0: Topic Selection
    if st.session_state.step == 0:
        st.header("Step 1: Select a Topic")
        
        # Get topic suggestions
        if not hasattr(st.session_state, 'topic_suggestions'):
            with st.spinner("Generating topic suggestions..."):
                st.session_state.topic_suggestions = st.session_state.workflow.get_topic_suggestions()
        
        # Add a refresh button for topics
        refresh_col1, refresh_col2 = st.columns([3, 1])
        with refresh_col1:
            st.subheader("Suggested Topics")
        with refresh_col2:
            if st.button("🔄 Refresh", key="refresh_topics"):
                with st.spinner("Generating new topic suggestions..."):
                    # Update the workflow with current preferences
                    st.session_state.workflow.preferences = st.session_state.preferences
                    # Generate new suggestions
                    st.session_state.topic_suggestions = st.session_state.workflow.get_topic_suggestions()
                    st.success("Topics refreshed!")
        
        # Display topic options
        topic_cols = st.columns(3)
        for i, topic in enumerate(st.session_state.topic_suggestions):
            with topic_cols[i % 3]:
                if st.button(f"📝 {topic['title']}", key=f"topic_{i}"):
                    st.session_state.workflow.select_topic(topic)
                    st.session_state.step = 1
                    st.rerun()
                st.markdown(f"*{topic['description']}*")
        
        # Custom topic option
        st.subheader("Or Enter Your Own Topic")
        custom_topic = st.text_input("Custom Topic Title")
        custom_description = st.text_area("Brief Description")
        
        if st.button("Use Custom Topic", key="use_custom_topic") and custom_topic:
            custom_topic_obj = {"title": custom_topic, "description": custom_description}
            st.session_state.workflow.select_topic(custom_topic_obj)
            st.session_state.step = 1
            st.rerun()
    
    # Step 1: Research Phase
    elif st.session_state.step == 1:
        st.header("Step 2: Research Collection")
        st.subheader(f"Topic: {st.session_state.workflow.topic['title']}")
        
        if not hasattr(st.session_state.workflow, 'research_completed'):
            with st.spinner("Researching your topic..."):
                research_progress = st.progress(0)
                
                # Simulate progress updates
                for percent_complete in range(0, 101, 20):
                    research_progress.progress(percent_complete)
                    time.sleep(0.5)  # Simulating time for research
                
                st.session_state.workflow.conduct_research()
                st.session_state.workflow.research_completed = True
        
        # Display research summary
        st.subheader("Research Summary")
        research_tabs = st.tabs(["Key Points", "Sources", "Related Topics"])
        
        with research_tabs[0]:
            for point in st.session_state.workflow.research['key_points']:
                st.markdown(f"• {point}")
        
        with research_tabs[1]:
            for source in st.session_state.workflow.research['sources']:
                st.markdown(f"- [{source['title']}]({source['url']})")
        
        with research_tabs[2]:
            for topic in st.session_state.workflow.research['related_topics']:
                st.markdown(f"• {topic}")
        
        if st.button("Continue to Script Creation", key="continue_to_script"):
            st.session_state.step = 2
            st.rerun()
    
    # Step 2: Script Creation
    elif st.session_state.step == 2:
        st.header("Step 3: Script Creation")
        
        if not hasattr(st.session_state.workflow, 'script_completed'):
            with st.spinner("Creating your podcast script..."):
                script_progress = st.progress(0)
                
                # Simulate progress updates
                for percent_complete in range(0, 101, 10):
                    script_progress.progress(percent_complete)
                    time.sleep(0.3)  # Simulating time for script creation
                
                st.session_state.workflow.create_script()
                st.session_state.workflow.script_completed = True
        
        # Display script
        st.subheader("Podcast Script")
        st.markdown(st.session_state.workflow.script)
        
        # Options for script editing
        st.subheader("Edit Script (optional)")
        edited_script = st.text_area("Edit Script", value=st.session_state.workflow.script, height=300)
        
        # Save edited script
        if edited_script != st.session_state.workflow.script:
            if st.button("Save Changes", key="save_script_changes"):
                st.session_state.workflow.script = edited_script
                st.success("Script updated!")
        
        if st.button("Continue to Content Check", key="continue_to_content_check"):
            st.session_state.step = 3
            st.rerun()
    
    # Step 3: Content Checking
    elif st.session_state.step == 3:
        st.header("Step 4: Content Check")
        
        if not hasattr(st.session_state.workflow, 'content_check_completed'):
            with st.spinner("Checking and refining content..."):
                check_progress = st.progress(0)
                
                # Simulate progress updates
                for percent_complete in range(0, 101, 20):
                    check_progress.progress(percent_complete)
                    time.sleep(0.4)  # Simulating time for content checking
                
                st.session_state.workflow.check_content()
                st.session_state.workflow.content_check_completed = True
        
        # Display content check results
        st.subheader("Content Check Results")
        
        check_tabs = st.tabs(["Grammar", "Clarity", "Content Issues", "Final Script"])
        
        with check_tabs[0]:
            if st.session_state.workflow.content_check['grammar_issues']:
                for issue in st.session_state.workflow.content_check['grammar_issues']:
                    st.markdown(f"• {issue}")
            else:
                st.success("No grammar issues found!")
        
        with check_tabs[1]:
            if st.session_state.workflow.content_check['clarity_issues']:
                for issue in st.session_state.workflow.content_check['clarity_issues']:
                    st.markdown(f"• {issue}")
            else:
                st.success("No clarity issues found!")
        
        with check_tabs[2]:
            if st.session_state.workflow.content_check['content_issues']:
                for issue in st.session_state.workflow.content_check['content_issues']:
                    st.markdown(f"• {issue}")
            else:
                st.success("No content issues found!")
        
        with check_tabs[3]:
            st.markdown(st.session_state.workflow.refined_script)
        
        if st.button("Continue to Audio Generation", key="continue_to_audio"):
            st.session_state.step = 4
            st.rerun()
    
    # Step 4: Audio Generation
    elif st.session_state.step == 4:
        st.header("Step 5: Audio Generation")
        
        # Voice options
        if not hasattr(st.session_state.workflow, 'selected_voice'):
            st.session_state.workflow.selected_voice = "en-US-Standard-D"  # Default voice
        
        voice_options = {
            "en-US-Standard-D": "US Male (Default)",
            "en-US-Standard-F": "US Female",
            "en-GB-Standard-B": "British Male",
            "en-GB-Standard-C": "British Female",
            "en-AU-Standard-B": "Australian Male",
            "en-AU-Standard-C": "Australian Female"
        }
        
        selected_voice = st.selectbox(
            "Select Voice", 
            list(voice_options.keys()),
            format_func=lambda x: voice_options[x],
            index=list(voice_options.keys()).index(st.session_state.workflow.selected_voice)
        )
        
        st.session_state.workflow.selected_voice = selected_voice
        
        # Audio generation
        if st.button("Generate Audio", key="generate_audio") or hasattr(st.session_state.workflow, 'audio_generating'):
            if not hasattr(st.session_state.workflow, 'audio_completed'):
                st.session_state.workflow.audio_generating = True
                
                with st.spinner("Generating audio... This may take a moment."):
                    audio_progress = st.progress(0)
                    
                    # Simulate progress updates
                    for percent_complete in range(0, 101, 5):
                        audio_progress.progress(percent_complete)
                        time.sleep(0.2)  # Simulating time for audio generation
                    
                    st.session_state.workflow.generate_audio()
                    st.session_state.workflow.audio_completed = True
        
        # Display audio if available
        if hasattr(st.session_state.workflow, 'audio_completed'):
            st.subheader("Podcast Audio")
            st.audio(st.session_state.workflow.audio_path)
            
            if st.button("Continue to Promotion", key="continue_to_promotion"):
                st.session_state.step = 5
                st.rerun()
    
    # Step 5: Promotion Generation
    elif st.session_state.step == 5:
        st.header("Step 6: Promotion Content")
        
        if not hasattr(st.session_state.workflow, 'promotion_completed'):
            with st.spinner("Generating promotion content..."):
                promo_progress = st.progress(0)
                
                # Simulate progress updates
                for percent_complete in range(0, 101, 20):
                    promo_progress.progress(percent_complete)
                    time.sleep(0.3)  # Simulating time for promotion content generation
                
                st.session_state.workflow.generate_promotion()
                st.session_state.workflow.promotion_completed = True
        
        # Display promotion content
        st.subheader("Social Media Content")
        
        promo_cols = st.columns(2)
        
        with promo_cols[0]:
            st.markdown("### Title")
            st.markdown(f"**{st.session_state.workflow.promotion['title']}**")
            
            st.markdown("### Post")
            st.markdown(st.session_state.workflow.promotion['post'])
        
        with promo_cols[1]:
            st.markdown("### Summary")
            st.markdown(st.session_state.workflow.promotion['summary'])
            
            st.markdown("### Hashtags")
            st.markdown(", ".join(st.session_state.workflow.promotion['hashtags']))
        
        if st.button("Continue to Email Distribution", key="continue_to_email"):
            st.session_state.step = 6
            st.rerun()
    
    # Step 6: Email Distribution
    elif st.session_state.step == 6:
        st.header("Step 7: Email Distribution")
        
        # Display subscribers from file if exists
        subscribers = []
        if os.path.exists("subscribers.txt"):
            with open("subscribers.txt", "r") as f:
                subscribers = [line.strip() for line in f.readlines() if line.strip()]
        
        # Show subscriber information
        if subscribers:
            st.write(f"Your podcast will be sent to {len(subscribers)} subscribers.")
            
            # Show sample of subscribers
            if len(subscribers) > 5:
                st.write(f"Sample subscribers: {', '.join(subscribers[:5])}...")
            else:
                st.write(f"Subscribers: {', '.join(subscribers)}")
        else:
            st.warning("You don't have any subscribers yet. Add some in the sidebar.")
        
        # Email preview
        st.subheader("Email Preview")
        st.markdown(f"**Subject:** New Podcast Episode: {st.session_state.workflow.promotion['title']}")
        
        email_body = f"""
        Hello Podcast Subscriber!

        We're excited to share our latest podcast episode with you:

        **{st.session_state.workflow.promotion['title']}**

        {st.session_state.workflow.promotion['summary']}

        Listen now at [Your Podcast Link]

        Thanks for subscribing!
        """
        
        st.markdown(email_body)
        
        # Send email button
        if st.button("Send to Subscribers", key="send_to_subscribers"):
            if subscribers:
                with st.spinner("Sending emails to subscribers..."):
                    send_result = st.session_state.workflow.send_emails(subscribers)
                    if send_result:
                        st.success(f"Emails sent to {len(subscribers)} subscribers!")
                    else:
                        st.error("Failed to send emails. Please check your email configuration.")
                
                # Save podcast to history
                st.session_state.workflow.save_podcast()
                st.session_state.podcasts = load_podcasts(st.session_state.user_id)
                
                st.session_state.step = 7
                st.rerun()
            else:
                st.error("No subscribers to send to. Add some subscribers first.")
    
    # Step 7: Completion
    elif st.session_state.step == 7:
        st.header("Podcast Creation Complete! 🎉")
        
        st.success("Your podcast has been created and distributed successfully!")
        
        # Summary of created podcast
        st.subheader("Podcast Summary")
        st.write(f"**Title:** {st.session_state.workflow.promotion['title']}")
        st.write(f"**Topic:** {st.session_state.workflow.topic['title']}")
        
        # Play audio
        st.subheader("Listen to Your Podcast")
        st.audio(st.session_state.workflow.audio_path)
        
        # Options for what to do next
        st.subheader("What's Next?")
        next_cols = st.columns(3)
        
        with next_cols[0]:
            if st.button("Create Another Podcast", key="create_another_podcast"):
                # Reset workflow and go back to step 0
                st.session_state.step = 0
                st.session_state.workflow = None
                st.session_state.current_podcast = None
                
                # Clear any cached suggestions
                if hasattr(st.session_state, 'topic_suggestions'):
                    delattr(st.session_state, 'topic_suggestions')
                
                st.rerun()
        
        with next_cols[1]:
            if st.button("View Podcast History", key="view_history_final"):
                st.session_state.show_history = True
                st.rerun()
        
        with next_cols[2]:
            if st.button("Edit Preferences", key="edit_preferences_final"):
                st.session_state.show_history = False
                # The preferences panel is always visible in the sidebar
                st.rerun()
