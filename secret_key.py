from django.core.management.utils import get_random_secret_key

# Generate a new secret key
secret_key = get_random_secret_key()

# Print or use the generated secret key
print("Generated Secret Key:", secret_key)
