# profile-management-app/app.py
from flask import Flask, request, jsonify, send_from_directory, abort
from flask_cors import CORS
import os
from supabase import create_client, Client, SupabaseRealtimeCallback # Corrected import if needed
from supabase.lib.client_options import ClientOptions # If needed for options
import requests
import logging
from dotenv import load_dotenv
import time # For retry delay

load_dotenv()

app = Flask(__name__, static_folder='frontend')
CORS(app) # Configure CORS appropriately for your frontend URL in production
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'change-this-in-production!')

# --- Supabase Setup ---
supabase_url: str = os.environ.get("SUPABASE_URL")
# Use Anon key by default, switch to SERVICE_ROLE if needed and secure it
supabase_key: str = os.environ.get("SUPABASE_KEY")
if not supabase_url or not supabase_key:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables.")
# You might need ClientOptions depending on your supabase-py version and needs
# options: ClientOptions = ClientOptions(...)
supabase: Client = create_client(supabase_url, supabase_key) #, options=options)
# Specify your Supabase table name (assuming it exists and matches schema provided)
PROFILE_TABLE_NAME = 'profiles' # CHANGE IF YOUR TABLE NAME IS DIFFERENT

# --- User Progress API URL ---
USER_PROGRESS_URL = os.environ.get("USER_PROGRESS_API_URL")
if not USER_PROGRESS_URL:
     raise ValueError("USER_PROGRESS_API_URL must be set.")

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

# --- Helper: Call User Progress Service ---
def sync_user_to_progress_service(user_id: str, email: str, full_name: Optional[str]):
    """Tries to POST user to User Progress Service with retry logic."""
    payload = {"id": user_id, "email": email, "full_name": full_name}
    endpoint = f"{USER_PROGRESS_URL}/users/"
    retries = 1 # Try original + 1 retry
    delay = 1 # seconds

    for attempt in range(retries + 1):
        try:
            response = requests.post(endpoint, json=payload, timeout=10)
            if response.status_code == status.HTTP_201_CREATED or response.status_code == status.HTTP_200_OK: # 200 if user already existed
                logging.info(f"Successfully synced user {user_id} to User Progress Service (Attempt {attempt + 1}). Status: {response.status_code}")
                return True
            elif response.status_code == status.HTTP_409_CONFLICT: # If API returns 409 for existing
                logging.warning(f"User {user_id} already exists in User Progress Service (Attempt {attempt + 1}).")
                return True # Treat as success
            else:
                 # Log other client/server errors
                 logging.error(f"Attempt {attempt + 1}: Failed to sync user {user_id} to User Progress. Status: {response.status_code}, Body: {response.text}")
                 # If it's the last attempt, log final failure
                 if attempt == retries:
                      logging.error(f"Max retries exceeded for syncing user {user_id}. Accepting inconsistency.")
                      return False
                 # Wait before retrying for transient issues
                 time.sleep(delay)

        except requests.exceptions.RequestException as e:
            logging.error(f"Attempt {attempt + 1}: Network/Connection error syncing user {user_id}: {e}")
            if attempt == retries:
                 logging.error(f"Max retries exceeded for syncing user {user_id} due to connection errors. Accepting inconsistency.")
                 return False
            time.sleep(delay) # Wait before retrying

    return False # Should only be reached if loop logic is flawed

# --- API Endpoints ---
@app.route('/api/profiles/<user_id>', methods=['GET'])
def get_profile(user_id):
    """Gets profile data directly from Supabase."""
    try:
        # Ensure PROFILE_TABLE_NAME is correct
        response = supabase.table(PROFILE_TABLE_NAME).select("*").eq('id', user_id).maybe_single().execute()
         # maybe_single() returns None if not found, raises PostgrestError on db errors
        if response.data:
             return jsonify(response.data)
        else:
             # User exists in Supabase Auth but not in profile table? Or just doesn't exist?
             # Check Supabase Auth if needed, or just return 404 based on profile table
             return jsonify({"message": "Profile data not found"}), 404
    except Exception as e:
         # Catch PostgrestError specifically if possible based on library version
         logging.error(f"Error fetching profile {user_id} from Supabase: {e}")
         return jsonify({"message": "Error fetching profile data"}), 500


@app.route('/api/profiles', methods=['POST'])
def handle_profile_creation_trigger():
    """
    Endpoint triggered after Supabase registration.
    Expects Supabase User ID, Email, and potentially other profile data.
    Creates entry in Supabase 'profiles' table and syncs user to Progress service.
    """
    data = request.get_json()
    if not data:
        abort(400, description="Invalid JSON payload.")

    user_id = data.get('id')
    email = data.get('email')
    first_name = data.get('first_name') # Example optional fields
    last_name = data.get('last_name')

    if not user_id or not email:
        abort(400, description="Required fields 'id' and 'email' missing.")

    # 1. Prepare data for Supabase 'profiles' table insert
    profile_payload = {k: v for k, v in data.items() if v is not None} # Use provided data
    profile_payload['id'] = user_id # Ensure ID is set correctly
    profile_payload['email'] = email # Ensure email is set

    try:
        # Check if profile already exists for this ID
        existing_profile = supabase.table(PROFILE_TABLE_NAME).select("id").eq('id', user_id).maybe_single().execute()

        if existing_profile.data:
             logging.warning(f"Profile for user {user_id} already exists in Supabase table '{PROFILE_TABLE_NAME}'. Skipping insert.")
             # Optionally: Proceed to sync to User Progress Service anyway to ensure consistency
             # success = sync_user_to_progress_service(user_id, email, f"{first_name or ''} {last_name or ''}".strip())
             # return jsonify({"message": "Profile already exists", "user_id": user_id}), 200

             # For now, let's treat existing profile as non-error and don't re-sync automatically
             return jsonify({"message": "Profile already exists", "user_id": user_id}), 200


        # Profile doesn't exist, insert it
        insert_response = supabase.table(PROFILE_TABLE_NAME).insert(profile_payload).execute()

        # Check response - specific checks depend on supabase-py version
        if not hasattr(insert_response, 'data') or not insert_response.data :
             # Attempt to get error details if possible
             error_detail = "Unknown error"
             if hasattr(insert_response, 'error') and insert_response.error:
                  error_detail = str(insert_response.error)
             logging.error(f"Failed to insert profile for {user_id} into Supabase table '{PROFILE_TABLE_NAME}'. Response: {error_detail}")
             raise Exception(f"Supabase insert failed: {error_detail}") # Raise to trigger general error handling

        logging.info(f"Successfully created profile for {user_id} in Supabase table '{PROFILE_TABLE_NAME}'.")

        # 2. Sync to User Progress Service
        full_name = f"{first_name or ''} {last_name or ''}".strip()
        sync_success = sync_user_to_progress_service(user_id, email, full_name)

        if not sync_success:
             # Logged in helper, decided to accept inconsistency
             return jsonify({"message": "Profile created in Supabase, but failed to sync to progress service", "user_id": user_id}), 207 # Multi-Status
        else:
             return jsonify({"message": "Profile created and synced successfully", "user_id": user_id}), 201

    except Exception as e:
         # Catch Supabase errors (PostgrestError?) or other exceptions
         logging.error(f"Error processing profile creation trigger for user {user_id}: {e}", exc_info=True)
         # Provide a generic error response
         return jsonify({"message": f"Server error processing profile creation: {e}"}), 500


@app.route('/api/profiles/<user_id>', methods=['PUT'])
def update_profile(user_id):
    """Updates profile data in Supabase."""
    data = request.get_json()
    if not data:
        abort(400, description="Invalid JSON payload.")

    # Prepare payload, prevent updating ID or email
    update_payload = {k: v for k, v in data.items() if k not in ['id', 'email', 'created_at', 'updated_at']}
    if not update_payload:
        return jsonify({"message": "No updatable profile data provided"}), 400

    try:
        response = supabase.table(PROFILE_TABLE_NAME).update(update_payload).eq('id', user_id).execute()

        # Check if the update was successful. Response structure varies.
        # Check if data exists and potentially if it indicates rows affected if available
        # If maybe_single() approach was used for get, we might need to check count or similar
        # Assuming a basic check here:
        if hasattr(response, 'error') and response.error:
             logging.error(f"Supabase error updating profile {user_id}: {response.error}")
             # Check if error indicates "not found" vs other errors
             if "Could not find" in str(response.error): # Example check
                  return jsonify({"message": "Profile not found"}), 404
             else:
                  return jsonify({"message": f"Failed to update profile: {response.error}"}), 500

        # Heuristic: If no error and maybe data is present, assume success
        # A better check might involve getting the count or checking response structure precisely
        logging.info(f"Successfully updated profile for {user_id} in Supabase.")

        # Optional: Sync relevant updates to User Progress Service
        # ... (add logic similar to sync_user_to_progress_service if needed, calling PUT) ...

        # Fetch and return updated profile?
        updated_profile = supabase.table(PROFILE_TABLE_NAME).select("*").eq('id', user_id).maybe_single().execute()
        return jsonify(updated_profile.data if updated_profile.data else {"message": "Profile updated successfully, but could not fetch result"}), 200

    except Exception as e:
        logging.error(f"Error updating profile {user_id}: {e}", exc_info=True)
        return jsonify({"message": "Server error updating profile"}), 500


@app.route('/api/profiles/<user_id>/progress', methods=['GET'])
def get_user_progress_proxy(user_id):
    """Gets user progress data by calling the User Progress Service."""
    # Optional: Verify user exists in Supabase first
    try:
         profile = supabase.table(PROFILE_TABLE_NAME).select('id').eq('id', user_id).maybe_single().execute()
         if not profile.data:
              return jsonify({"message": "Profile not found for this user"}), 404
    except Exception as e:
         logging.error(f"Error checking profile {user_id} before getting progress: {e}")
         return jsonify({"message": "Error verifying user profile"}), 500

    # Call User Progress Service endpoint (e.g., the one returning UserProgressRead)
    endpoint = f"{USER_PROGRESS_URL}/users/{user_id}/progress/" # Use the combined endpoint
    try:
        response = requests.get(endpoint, timeout=10)
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
        return jsonify(response.json())
    except requests.exceptions.HTTPError as err:
        status_code = err.response.status_code
        if status_code == 404:
             logging.warning(f"User progress not found for user {user_id} (HTTP 404 from progress service).")
             # Return specific structure or just the error message?
             return jsonify({"message": "User progress data not found"}), 404
        else:
             logging.error(f"HTTP error getting progress for {user_id}: Status {status_code}, Response: {err.response.text}")
             return jsonify({"message": f"Error from progress service (Status {status_code})"}), status_code
    except requests.exceptions.RequestException as e:
        logging.error(f"Network error getting progress for {user_id}: {e}")
        return jsonify({"message": "Could not connect to user progress service"}), 503 # Service Unavailable


# --- Serve Frontend --- (No changes needed from previous version)
@app.route('/', defaults={'path': 'index.html'})
@app.route('/<path:path>')
def serve_frontend(path):
    static_folder = app.static_folder or 'frontend'
    full_path = os.path.join(static_folder, path)
    if os.path.exists(full_path) and os.path.isfile(full_path):
         return send_from_directory(static_folder, path)
    index_path = os.path.join(static_folder, 'index.html')
    if os.path.exists(index_path):
         return send_from_directory(static_folder, 'index.html')
    else:
         abort(404, description="Frontend index.html not found")

# --- Run App ---
if __name__ == '__main__':
    # Use environment variable for port, default to 5001
    port = int(os.environ.get('PORT', 5001))
    # Debug should be False in production
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    app.run(debug=debug_mode, host='0.0.0.0', port=port)