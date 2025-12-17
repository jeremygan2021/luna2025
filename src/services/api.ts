import axios from 'axios';

const API_KEY = '123tangledup-ai';
const BASE_URL = ''; // Use relative path to leverage proxy
const DEVICE_ID = '1'; // As per curl example

export interface Todo {
  id: number;
  title: string;
  description: string;
  due_date: string;
  device_id: string;
  is_completed: boolean;
  completed_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface CreateTodoDto {
  title: string;
  description?: string;
  due_date?: string;
  device_id?: string;
}

export interface UpdateTodoDto {
  title?: string;
  description?: string;
  due_date?: string;
  is_completed?: boolean;
}

const api = axios.create({
  baseURL: BASE_URL,
  headers: {
    'accept': 'application/json',
    'X-API-Key': API_KEY,
  },
});

export const todoApi = {
  getTodos: async (skip = 0, limit = 100) => {
    const response = await api.get<Todo[]>('/api/todos/', {
      params: {
        skip,
        limit,
        device_id: DEVICE_ID,
      },
    });
    return response.data;
  },

  getTodo: async (id: number) => {
    const response = await api.get<Todo>(`/api/todos/${id}`);
    return response.data;
  },

  createTodo: async (data: CreateTodoDto) => {
    const response = await api.post<Todo>('/api/todos/', {
      ...data,
      device_id: data.device_id || DEVICE_ID,
    });
    return response.data;
  },

  updateTodo: async (id: number, data: UpdateTodoDto) => {
    const response = await api.put<Todo>(`/api/todos/${id}`, data);
    return response.data;
  },

  deleteTodo: async (id: number) => {
    const response = await api.delete(`/api/todos/${id}`);
    return response.data;
  },

  completeTodo: async (id: number) => {
    const response = await api.post<Todo>(`/api/todos/${id}/complete`);
    return response.data;
  },

  incompleteTodo: async (id: number) => {
    const response = await api.post<Todo>(`/api/todos/${id}/incomplete`);
    return response.data;
  },
};
