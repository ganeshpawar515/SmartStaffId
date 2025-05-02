import cv2
import face_recognition
import os
import sqlite3
class recognition:
    def __init__(self):
        self.is_running=False
    def start_recognition(self):
        # Load known faces
        known_face_encodings = []
        known_face_names = []
        images_folder = 'images'

        # Iterate over all files in the directory
        for filename in os.listdir(images_folder):
            if filename.endswith(('.jpg', '.jpeg', '.png')):  # Check for image file extensions
                # Load the image file
                image_path = os.path.join(images_folder, filename)
                known_face_image = face_recognition.load_image_file(image_path)
                
                # Get the face encoding for the image
                face_encodings = face_recognition.face_encodings(known_face_image)
                if len(face_encodings) > 0:
                    known_face_encodings.append(face_encodings[0])
                    known_face_names.append(os.path.splitext(filename)[0])
                else:
                    print(f"No face found in {filename}")


        # Initialize some variables
        face_locations = []
        face_encodings = []
        face_names = []

        # Initialize the camera
        self.cap = cv2.VideoCapture(0)
        self.is_running=True
        console_printed=[]
        while self.is_running:
            # Capture frame-by-frame
            ret, frame = self.cap.read()
            
            # Find all face locations and face encodings in the frame
            face_locations = face_recognition.face_locations(frame)
            face_encodings = face_recognition.face_encodings(frame, face_locations)
            
            face_names = []
            for face_encoding in face_encodings:
                # See if the face is a match for the known face(s)
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                name = "Unknown"
                
                # If a match is found, use the known face name
                if True in matches:
                    first_match_index = matches.index(True)
                    name = known_face_names[first_match_index]
                
                face_names.append(name)
            
            # Display the results
            for (top, right, bottom, left), name in zip(face_locations, face_names):
                # Draw a box around the face
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                
                # Draw a label with a name below the face
                cv2.rectangle(frame, (left, bottom+25), (right, bottom-25), (0, 255, 0), cv2.FILLED)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(frame, name, (left + 6, bottom - 6), font, 0.5, (0, 0, 0), 1)
                #print(name)
                if name!="Unknown":
                    name, position, e_info=self.fetch_employee_info(int(name),'employee.db')
                    if  name not in console_printed:
                        print(e_info)
                        console_printed.append(name)
                    cv2.putText(frame, name, (left + 6, bottom+10), font, 0.5, (0, 0, 0), 1)
                    cv2.putText(frame, position, (left + 6, bottom+25), font, 0.5, (0, 0, 0), 1)
            
            # Display the frame with recognized faces
            cv2.imshow('Face Recognition', frame)
            
            # Break the loop when 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        self.cap.release()
        cv2.destroyAllWindows()
    
    def stop_recognition(self):
        # Release the camera and close all OpenCV windows
        self.is_running=False
    def fetch_employee_info(self,employee_id, db_file):
        try:
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM employees WHERE id=?", (employee_id,))
            employee_info = cursor.fetchone()
            conn.close()
            #print("info:",employee_info)
            #print("info:",type(employee_info))
            #print("info:",employee_info[1])
            name=employee_info[1]
            position=employee_info[3]
            info=employee_info
            return name, position,info
        except Exception as e:
            print(f"Error fetching employee info: {e}")
            
