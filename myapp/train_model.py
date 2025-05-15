from ai_model import HealthcareAI
import os

def train_model():
    model = HealthcareAI()
    
    # Check if model is already trained
    if model.load_model():
        print("Model already trained and loaded successfully!")
        return model
    
    # Train new model if not exists
    pdf_folder = os.path.join(os.path.dirname(__file__), 'training_pdfs')
    
    if not os.path.exists(pdf_folder):
        os.makedirs(pdf_folder)
    
    num_files = model.train_from_folder(pdf_folder)
    print(f"Successfully processed {num_files} PDF files")
    
    # Save the trained model
    model.save_model()
    print("Model trained and saved successfully!")
    
    return model

if __name__ == "__main__":
    train_model()