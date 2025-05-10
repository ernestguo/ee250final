# ee250final
Group Members:
Joel Sedillo
Ernest Guo

Demo video: https://www.youtube.com/watch?v=uCm5rY9pBLs

Compile/Execute program(s):
Frontend Execute - 
    - Open terminal
    - cd /path/to/the/project
    - enter: python3 -m http.server 8000
    - Open default browser and search: http://localhost:8000/frontend.html

Backend Execute -
    - Headless
        - Create systemd service
        - Executes /path/to/python3 /path/to/the/project/backend/timer.py
        - Enable service
    - Main terminal
        - python3 /path/to/the/project/backend/timer.py
