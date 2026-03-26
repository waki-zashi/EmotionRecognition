package main

type ImageTask struct {
	TaskID    string `json:"task_id"`
	UserID    int    `json:"user_id"`
	FileName  string `json:"file_name"`
	ImageData string `json:"image_data"`
}
