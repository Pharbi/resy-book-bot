import logging
from typing import Dict

from firebase_admin import App as FirebaseAdminApp
from firebase_admin.auth import Client as FirebaseAuthClient, UserRecord
from firebase_admin.auth import EmailAlreadyExistsError
from google.cloud.firestore import Client as FirestoreClient


class AccountHandler:

	def __init__(self, firebase_admin: FirebaseAdminApp, firestore_client: FirestoreClient, logger: logging.Logger, email: str):
		self.firebase_auth = FirebaseAuthClient(firebase_admin)
		self.firestore_client = firestore_client
		self.account_handler_logger = logger
		self.bot_email = email

	def create_new_user_account(self, user_registration: Dict):
		try:
			firebase_user = self.firebase_auth.create_user(
				display_name=user_registration["first_name"],
				email=user_registration["email"],
				password=user_registration["password"],
				phone_number=user_registration["phone_number"]
			)
			return firebase_user
		except EmailAlreadyExistsError as user_exists:
			self.account_handler_logger.error(f"{user_exists}:{user_registration['email']}")
			return None

	def get_user_id(self, email):
		firebase_user: UserRecord = self.firebase_auth.get_user_by_email(email)
		if firebase_user.uid:
			return firebase_user.uid
		return None

	def get_user_account(self, user_id):
		firebase_user: UserRecord = self.firebase_auth.get_user(user_id)
		if firebase_user:
			return firebase_user
		return None

	def get_user_email(self, user_id):
		firebase_user: UserRecord = self.firebase_auth.get_user(user_id)
		if firebase_user:
			return firebase_user.email
		return None

	def save_resy_token(self, user_id, user_token):
		self.firestore_client.collection("resy_tokens").document(user_id).create({"_token": user_token})
		return

	def remove_resy_token(self, user_id):
		self.firestore_client.collection("resy_tokens").document(user_id).delete()
		return

	def get_resy_token(self, user_id):
		resy_token = self.firestore_client.collection('resy_tokens').document(user_id).get()
		if resy_token.exists:
			token = resy_token.to_dict()
			return token["_token"]
		return None

	def valid_resy_token(self, user_id):
		return True if self.get_resy_token(user_id) else False

        def delete_reservation_request(self, uid, task_id):
                try:
                        self.firestore_client.collection(
                                f"reservation_task_request/{uid}/tasks"
                        ).document(task_id).delete()
                except Exception as e:
                        self.account_handler_logger.error(f"Error deleting reservation request, it may have already been deleted: {e}")
                return

	def send_email(self, email, subject, body):
		self.account_handler_logger.info(f"Sending email related to user about: {subject}")
		self.firestore_client.collection("mail").add({
			"from": f"Resy Bot <{self.bot_email}>",
			"to": email,
			"message": {
				"subject": subject,
				"html": body
			}
		})
		return