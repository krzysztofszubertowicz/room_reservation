export interface Room {
  id?: number;
  name: string;
  seat_count: number;
  room_type?: { name: string };
  building: string;
  floor: number;
  description: string;
  equipment: number[];
  type_id: number;
}
