"use client";
import { useState, useEffect } from "react";
import AddRoomForm from "./AddRoomForm";
import EditRoomForm from "./EditRoomForm";
import { Room } from "./types";

export default function RoomTable({ rooms }: { rooms: Room[] }) {
  const [selectedRoom, setSelectedRoom] = useState<Room | null>(null);
  const [showAddForm, setShowAddForm] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [roomList, setRoomList] = useState<Room[]>(rooms);

  useEffect(() => {
    setRoomList(rooms);
  }, [rooms]);

  const handleClose = () => {
    setSelectedRoom(null);
    setShowAddForm(false);
  };

  const handleSave = async () => {
    setSelectedRoom(null);
    setShowAddForm(false);
    // Odśwież listę sal po dodaniu/edycji
    setIsLoading(true);
    try {
      const res = await fetch("http://localhost:8000/rooms");
      const data = await res.json();
      setRoomList(data);
    } catch (err) {
      console.error("Błąd przy pobieraniu sal:", err);
    }
    setIsLoading(false);
  };

  return (
    <>
      <div className="flex justify-end mb-4">
        <button
          className="px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded"
          onClick={() => setShowAddForm(true)}
        >
          Dodaj salę
        </button>
      </div>
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
          {roomList.map((room) => (
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

      {showAddForm && (
        <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-10 z-50">
          <div className="bg-white p-6 rounded-xl w-full max-w-md shadow-lg">
            <h2 className="text-xl font-semibold mb-4">Dodaj salę</h2>
            <AddRoomForm onClose={handleClose} onSave={handleSave} />
          </div>
        </div>
      )}
      {isLoading && (
        <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-20 z-50">
          <div className="bg-white p-4 rounded shadow">Ładowanie...</div>
        </div>
      )}
    </>
  );
}
