graph TD

subgraph API Endpoints
    A["/image (POST)"] --> B["Initiate OCR Task<br>ocr_create_task"]
end

subgraph Client
    C[Client] --> A

    %% J --> K["Retrieve OCR Result<br>ocr_task_result"]
    %% D --> J
end
    B --> EE
subgraph Redis Broker
 EE[TASK QUEUE]
end

    EE --> E


subgraph Main Tasks
    E["Check single or multiple image"] -->|batch images| F["Create Subtasks"]
    KK["OCR"]
end

subgraph Sub Tasks
    F --> DD["OCR"]
    F --> DD
    
end

subgraph Redis
     I[DB]
end

DD --> |result| I
DD --> |result| I
E -->|single image| KK
KK --> |result| I


style A fill:#99ccff,stroke:#333,stroke-width:2px
style B fill:#66cc66,stroke:#333,stroke-width:2px
style E fill:#ffcc66,stroke:#333,stroke-width:2px
style C fill:#ffcc66,stroke:#333,stroke-width:2px
style F fill:#ff9966,stroke:#333,stroke-width:2px
style I fill:#cccccc,stroke:#333,stroke-width:2px

