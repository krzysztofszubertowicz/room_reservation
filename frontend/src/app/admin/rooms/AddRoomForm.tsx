import { useState, useCallback } from "react";
import { Room } from "./types";

export default function AddRoomForm({
  onClose,
  onSave,
}: {
  onClose: () => void;
  onSave: () => void;
}) {
  const [formData, setFormData] = useState<Room>({
    name: "",
    seat_count: 0,
    type_id: 1,
    building: "",
    floor: 0,
    description: "",
    equipment: [],
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
      setFormData((prev) => ({ ...prev, [e.target.name]: e.target.value }));
    },
    []
  );

  const handleTypeIdChange = useCallback(
    (e: React.ChangeEvent<HTMLSelectElement>) => {
      setFormData((prev) => ({ ...prev, type_id: Number(e.target.value) }));
    },
    []
  );

  const handleSubmit = useCallback(
    async (event: React.FormEvent) => {
      event.preventDefault();
      setIsSubmitting(true);
      setError(null);
      try {
        const res = await fetch("http://localhost:8000/rooms", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${localStorage.getItem("access_token")}`,
          },
          body: JSON.stringify({
            name: formData.name,
            seat_count: Number(formData.seat_count),
            type_id: formData.type_id,
            building: formData.building,
            floor: formData.floor,
            description: formData.description,
            equipment: formData.equipment,
          }),
        });
        if (!res.ok) {
          const errText = await res.text();
          throw new Error(errText || "Błąd dodawania sali");
        }
        onSave();
      } catch (err: unknown) {
        if (err instanceof Error) {
          setError(err.message);
        } else {
          setError("Wystąpił nieznany błąd");
        }
      }
      setIsSubmitting(false);
      return false;
    },
    [formData, onSave]
  );

  return (
    <form onSubmit={handleSubmit}>
      <input
        name="name"
        value={formData.name}
        onChange={handleChange}
        className="w-full border p-2 rounded mb-3"
        placeholder="Nazwa sali"
        required
      />
      <input
        name="seat_count"
        type="number"
        value={formData.seat_count}
        onChange={handleChange}
        className="w-full border p-2 rounded mb-3"
        placeholder="Pojemność"
        required
      />
      <input
        name="building"
        value={formData.building}
        onChange={handleChange}
        className="w-full border p-2 rounded mb-3"
        placeholder="Budynek"
        required
      />
      <input
        name="floor"
        value={formData.floor}
        onChange={handleChange}
        className="w-full border p-2 rounded mb-3"
        placeholder="Piętro"
        required
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
        onChange={handleTypeIdChange}
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
          type="button"
          onClick={onClose}
          className="px-4 py-2 border rounded hover:bg-gray-100 text-gray-600"
          disabled={isSubmitting}
        >
          Anuluj
        </button>
        <button
          type="submit"
          className="px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded"
          disabled={isSubmitting}
        >
          {isSubmitting ? "Zapisywanie..." : "Dodaj"}
        </button>
      </div>
      {error && <div className="text-red-500 mt-2">{error}</div>}
    </form>
  );
}
