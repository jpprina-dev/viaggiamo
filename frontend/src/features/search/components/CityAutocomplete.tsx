/**
 * City autocomplete input component with keyboard navigation
 */

'use client'

import { useEffect, useRef, useState } from 'react'
import { LocalitySuggestion, useCityAutocomplete } from '../hooks/useCityAutocomplete'

interface CityAutocompleteProps {
  type: 'origin' | 'destination'
  value: string
  onChange: (value: string) => void
  onSelectLocality?: (locality: LocalitySuggestion) => void
  onBlur?: () => void
  placeholder?: string
  error?: string
  disabled?: boolean
  className?: string
  leftIcon?: React.ReactNode
  rightIcon?: React.ReactNode
}

export function CityAutocomplete({
  type,
  value,
  onChange,
  onSelectLocality,
  onBlur,
  placeholder,
  error,
  disabled = false,
  className = '',
  leftIcon,
  rightIcon,
}: CityAutocompleteProps) {
  const { suggestions, loading, fetchSuggestions } = useCityAutocomplete()
  const [isOpen, setIsOpen] = useState(false)
  const [selectedIndex, setSelectedIndex] = useState(-1)
  const inputRef = useRef<HTMLInputElement>(null)
  const dropdownRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node) &&
        !inputRef.current?.contains(event.target as Node)
      ) {
        setIsOpen(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value
    onChange(newValue)
    setSelectedIndex(-1)
    
    // Only fetch and show suggestions when user is actively typing
    if (newValue && newValue.length >= 2) {
      fetchSuggestions(newValue)
      setIsOpen(true)
    } else {
      setIsOpen(false)
    }
  }
  
  const handleInputFocus = () => {
    if (value && value.length >= 2 && suggestions.length > 0) {
      setIsOpen(true)
    }
  }

  const handleSelectSuggestion = (suggestion: LocalitySuggestion) => {
    onChange(suggestion.displayName)
    onSelectLocality?.(suggestion)
    setIsOpen(false)
    setSelectedIndex(-1)
    inputRef.current?.blur()
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (!isOpen || suggestions.length === 0) return

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault()
        setSelectedIndex((prev) =>
          prev < suggestions.length - 1 ? prev + 1 : prev
        )
        break
      case 'ArrowUp':
        e.preventDefault()
        setSelectedIndex((prev) => (prev > 0 ? prev - 1 : -1))
        break
      case 'Enter':
        e.preventDefault()
        if (selectedIndex >= 0 && selectedIndex < suggestions.length) {
          handleSelectSuggestion(suggestions[selectedIndex]!)
        }
        break
      case 'Escape':
        setIsOpen(false)
        setSelectedIndex(-1)
        break
    }
  }

  const showDropdown = isOpen && suggestions.length > 0

  return (
    <div className="relative">
      {leftIcon && (
        <div className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 z-10">
          {leftIcon}
        </div>
      )}

      <input
        ref={inputRef}
        type="text"
        value={value}
        onChange={handleInputChange}
        onFocus={handleInputFocus}
        onBlur={onBlur}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        disabled={disabled}
        className={
          className ||
          `w-full rounded-lg border py-3 text-base outline-none transition-colors ${
            leftIcon ? 'pl-10' : 'pl-4'
          } ${
            rightIcon || loading ? 'pr-10' : 'pr-4'
          } ${
            error
              ? 'border-red-500 focus:border-red-600'
              : 'border-gray-300 focus:border-primary-600'
          } ${disabled ? 'cursor-not-allowed bg-gray-100' : 'bg-white'}`
        }
        aria-label={`${type} city`}
        aria-autocomplete="list"
        aria-controls={`${type}-suggestions`}
        aria-expanded={showDropdown}
        role="combobox"
      />

      {loading && !rightIcon && (
        <div className="absolute right-3 top-1/2 -translate-y-1/2">
          <div className="h-5 w-5 animate-spin rounded-full border-2 border-gray-300 border-t-primary-600" />
        </div>
      )}

      {rightIcon && !loading && (
        <div className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400">
          {rightIcon}
        </div>
      )}

      {loading && rightIcon && (
        <div className="absolute right-3 top-1/2 -translate-y-1/2">
          <div className="h-5 w-5 animate-spin rounded-full border-2 border-gray-300 border-t-primary-600" />
        </div>
      )}

      {showDropdown && (
        <div
          ref={dropdownRef}
          id={`${type}-suggestions`}
          role="listbox"
          className="absolute z-50 mt-1 max-h-60 w-full overflow-auto rounded-lg border border-gray-200 bg-white shadow-lg"
        >
          {suggestions.map((suggestion, index) => (
            <button
              key={suggestion.id}
              type="button"
              role="option"
              aria-selected={index === selectedIndex}
              className={`w-full px-4 py-3 text-left transition-colors ${
                index === selectedIndex
                  ? 'bg-primary-100 text-primary-700'
                  : 'hover:bg-gray-50'
              }`}
              onClick={() => handleSelectSuggestion(suggestion)}
              onMouseEnter={() => setSelectedIndex(index)}
            >
              {suggestion.displayName}
            </button>
          ))}
        </div>
      )}

      {error && (
        <p className="mt-1 text-sm text-red-600" id={`${type}-error`}>
          {error}
        </p>
      )}
    </div>
  )
}

