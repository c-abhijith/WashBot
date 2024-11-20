# CarWash API

A Flask-based REST API for a car wash booking system with payment integration and image handling.

Postman documentation:https://orange-eclipse-887429.postman.co/workspace/946e5419-f0a1-4509-8221-995adc670dd9/overview
## Features

- 🔐 JWT Authentication
- 👥 User Management (Admin/Staff/User roles)
- 🚗 Vehicle Management
- 📅 Booking System
- 💳 Multiple Payment Gateways (Stripe, PayPal, Razorpay)
- 🖼️ Image Upload (Cloudinary)
- 📝 Service Management
- 🔄 Booking Status Workflow

## Tech Stack

- Python 3.8+
- Flask
- PostgreSQL
- SQLAlchemy
- JWT
- Cloudinary
- Payment Gateways (Stripe, PayPal, Razorpay)

## Prerequisites

- Python 3.8 or higher
- PostgreSQL
- Cloudinary account
- Payment gateway accounts (Stripe/PayPal/Razorpay)

## Installation

1. Clone the repository: 


# CarWash Application Documentation

## Application Overview

The CarWash Application is a comprehensive booking system designed for car wash businesses. It enables customers to book services, manage their vehicles, and make payments while providing staff and administrators with tools to manage bookings, services, and customer data.

## User Roles

### 1. Admin
- **Permissions**:
  - Full system access
  - Manage all users
  - Manage services and pricing
  - View all bookings
  - Cancel any booking
  - Access analytics
  - Manage staff accounts

### 2. Staff
- **Permissions**:
  - View assigned bookings
  - Update booking status
  - View customer details
  - View service details
  - Basic profile management

### 3. User (Customer)
- **Permissions**:
  - Manage personal profile
  - Add/manage vehicles
  - Book services
  - View booking history
  - Make payments
  - Cancel pending bookings

## Workflow Processes

### 1. Booking Flow
1. **Booking Creation**
   - User selects service
   - Chooses vehicle
   - Selects date and time
   - Makes payment
   - Booking status: 'pending'

2. **Booking Confirmation**
   - Staff reviews booking
   - Updates status to 'confirmed'
   - Customer receives confirmation

3. **Service Execution**
   - Staff updates status to 'startservice'
   - Service is performed
   - Status updated to 'complete'

4. **Cancellation Flow**
   - User can cancel 'pending' bookings
   - Admin can cancel any booking
   - Refund process initiated if applicable

### 2. Payment Flow
1. **Payment Initiation**
   - User selects payment method
   - Payment gateway initialized
   - Payment details collected

2. **Payment Processing**
   - Gateway processes payment
   - System verifies transaction
   - Booking confirmed on success

3. **Refund Process**
   - Admin initiates refund
   - Payment gateway processes refund
   - User notified of refund

## API Endpoints Documentation

### Authentication Endpoints

#### 1. User Registration 