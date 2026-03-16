import { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';

export const useListFilters = (list, extraParams = {}, listOptions = {}) => {
  const [searchParams, setSearchParams] = useSearchParams();

  const [search, setSearch] = useState(searchParams.get('search') || '');
  const [debouncedSearch, setDebouncedSearch] = useState(searchParams.get('search') || '');
  const [page, setPage] = useState(Number(searchParams.get('page')) || 1);

  // Debounce de búsqueda (400ms)
  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedSearch(search);
    }, 400);
    return () => clearTimeout(handler);
  }, [search]);

  // Sincronización con URL y llamada a API
  useEffect(() => {
    const urlParams = {};
    const apiParams = { page };

    if (debouncedSearch) {
      urlParams.search = debouncedSearch;
      apiParams.search = debouncedSearch;
    }

    if (page > 1) {
      urlParams.page = page.toString();
    }

    // Manejar filtros extra (ej: estado)
    Object.keys(extraParams).forEach((key) => {
      const value = extraParams[key];
      if (value) {
        urlParams[key] = value;
        apiParams[key] = value;
      }
    });

    setSearchParams(urlParams, { replace: true });
    list(apiParams, listOptions);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [debouncedSearch, page, list, setSearchParams, JSON.stringify(extraParams), JSON.stringify(listOptions)]);

  return { search, setSearch, page, setPage };
};