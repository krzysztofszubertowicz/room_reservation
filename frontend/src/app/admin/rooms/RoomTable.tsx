"use client";
import { useState, useEffect } from "react";

type Room = {
  id: number;
  name: string;
  seat_count: number;
  room_type: { name: string };
  building: string;
  floor: string;
  description: string;
  status: string | null;
};

export default function RoomTable({ rooms }: { rooms: Room[] }) {
  const [selectedRoom, setSelectedRoom] = useState<Room | null>(null);
  const handleClose = () => setSelectedRoom(null);
  const handleSave = () => {
    setSelectedRoom(null);
  };

  return (
    <>
      <table className="min-w-full bg-white rounded-lg shadow">
        <thead>
          <tr className="bg-gray-100 text-left">
            <th className="p-3">Nr</th>
            <th className="p-3">Typ</th>
            <th className="p-3">Pojemność</th>
            <th className="p-3">Budynek</th>
            <th className="p-3">Piętro</th>
            <th className="p-3">Opis</th>
            <th className="p-3"></th>
          </tr>
        </thead>
        <tbody>
          {rooms.map((room) => (
            <tr key={room.id} className="border border-gray-200">
              <td className="p-3">{room.name}</td>
              <td className="p-3">
                {room.room_type?.name
                  ? room.room_type.name.charAt(0).toUpperCase() +
                    room.room_type.name.slice(1)
                  : "Brak typu"}
              </td>
              <td className="p-3">{room.seat_count}</td>
              <td className="p-3">{room.building}</td>
              <td className="p-3">{room.floor}</td>
              <td className="p-3">{room.description}</td>
              <td className="p-3">
                <button
                  className="px-2 py-1 rounded-[6px] hover:bg-gray-200 transition"
                  onClick={() => setSelectedRoom(room)}
                >
                  Edytuj
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {selectedRoom && (
        <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-10 z-50">
          <div className="bg-white p-6 rounded-xl w-full max-w-md shadow-lg">
            <h2 className="text-xl font-semibold mb-4">Edytuj salę</h2>

            <EditRoomForm
              room={selectedRoom}
              onClose={handleClose}
              onSave={handleSave}
            />
          </div>
        </div>
      )}
    </>
  );
}

function EditRoomForm({
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
    const {
      id,
      room_type,
      seat_count,
      name,
      description,
      building,
      floor,
      status,
    } = formData;

    try {
      await fetch(`http://localhost:8000/rooms/${room.id}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
        body: JSON.stringify({
          status,
          floor,
          name,
          description,
          building,
          room_type: room_type.name,
          seat_count: Number(seat_count.toString()),
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
      <input
        name="room_type.name"
        value={formData.room_type.name}
        onChange={(e) =>
          setFormData({
            ...formData,
            room_type: { name: e.target.value },
          })
        }
        className="w-full border p-2 rounded mb-3"
        placeholder="Typ sali"
      />

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
