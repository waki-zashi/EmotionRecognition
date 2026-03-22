package protocol

type UserRequest struct {
	ID   string `json:"id"`
	Name string `json:"name"`
}

type UserResponse struct {
	Message string `json:"message"`
	Status  string `json:"status"`
}
