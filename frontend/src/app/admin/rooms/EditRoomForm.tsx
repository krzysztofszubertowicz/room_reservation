import { useState, useEffect } from "react";
import { Room } from "./types";

export default function EditRoomForm({
  room,
  onClose,
  onSave,
}: {
  room: Room;
  onClose: () => void;
  onSave: () => void;
}) {
  const [formData, setFormData] = useState<Room>(room);

  useEffect(() => {
    setFormData(room);
  }, [room]);

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    console.log("Submitting form with data:", formData);
    const { type_id, seat_count, name, description, building, floor } =
      formData;

    try {
      await fetch(`http://localhost:8000/rooms/${room.id}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
        body: JSON.stringify({
          name,
          description,
          building,
          type_id: Number(type_id.toString()),
          seat_count: Number(seat_count.toString()),
          floor: Number(floor.toString()),
        }),
      });
      onSave();
    } catch (error) {
      console.error("Error updating room:", error);
    }
    return false;
  };

  return (
    <div>
      <input
        name="name"
        value={formData.name}
        onChange={handleChange}
        className="w-full border p-2 rounded mb-3"
        placeholder="Nazwa sali"
      />
      <input
        name="seat_count"
        type="number"
        value={formData.seat_count}
        onChange={handleChange}
        className="w-full border p-2 rounded mb-3"
        placeholder="Pojemność"
      />
      <input
        name="building"
        value={formData.building}
        onChange={handleChange}
        className="w-full border p-2 rounded mb-3"
        placeholder="Budynek"
      />
      <input
        name="floor"
        value={formData.floor}
        onChange={handleChange}
        className="w-full border p-2 rounded mb-3"
        placeholder="Piętro"
      />
      <textarea
        name="description"
        value={formData.description}
        onChange={handleChange}
        className="w-full border p-2 rounded mb-3"
        placeholder="Opis"
      />
      <select
        name="type_id"
        value={formData.type_id}
        onChange={(e) =>
          setFormData({
            ...formData,
            type_id: Number(e.target.value),
          })
        }
        className="w-full border p-2 rounded mb-3"
      >
        <option value={1}>komputerowa</option>
        <option value={2}>graficzna</option>
        <option value={3}>programistyczna</option>
        <option value={4}>wykladowa</option>
        <option value={5}>duza wykladowa</option>
      </select>

      <div className="flex justify-end gap-2 mt-4">
        <button
          onClick={onClose}
          className="px-4 py-2 border rounded hover:bg-gray-100 text-gray-600"
        >
          Anuluj
        </button>
        <button
          onClick={handleSubmit}
          className="px-4 py-2 bg-green-500 hover:bg-green-600 text-white rounded"
        >
          Zapisz
        </button>
      </div>
    </div>
  );
}
