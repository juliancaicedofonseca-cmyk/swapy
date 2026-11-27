<?php

namespace App\Models;

use CodeIgniter\Model;

class ProductoModel extends Model
{
    protected $table = 'productos';
    protected $primaryKey = 'id_producto';
    
    protected $allowedFields = [
        'nombre_producto',
        'valor_estimado',
        'desc_producto',
        'imagen',
        'fk_id_categoria',
        'fk_cod_impulso',
        'fk_id_doc',
        'fk_id_usuario'
        
    ];

    protected $returnType = 'array';
    protected $useTimestamps = false;
    protected $skipValidation = true;

    public function obtenerCategorias()
    {
        $db = \Config\Database::connect();
        return $db->query("SELECT id_categoria, n_categoria FROM categorias ORDER BY id_categoria")->getResultArray();
    }

    public function obtenerTodos()
    {
        $db = \Config\Database::connect();
        $sql = "SELECT p.*, c.n_categoria, u.username, u.correo,
                       CASE WHEN up.estado IN ('activo', 'cancelado')
                                 AND (up.fecha_fin IS NULL OR up.fecha_fin > CURRENT_TIMESTAMP)
                            THEN 1 ELSE 0 END AS es_premium
                FROM productos p 
                LEFT JOIN categorias c ON p.fk_id_categoria = c.id_categoria 
                LEFT JOIN usuario u ON p.fk_id_usuario = u.id_usuario
                LEFT JOIN usuario_premium up ON up.id_usuario = u.id_usuario
                ORDER BY es_premium DESC,
                          CASE WHEN up.estado IN ('activo', 'cancelado')
                                    AND (up.fecha_fin IS NULL OR up.fecha_fin > CURRENT_TIMESTAMP)
                               THEN CASE up.plan WHEN '12 meses' THEN 3 WHEN '3 meses' THEN 2 WHEN '1 mes' THEN 1 ELSE 0 END
                               ELSE 0 END DESC,
                          p.id_producto DESC";
        return $db->query($sql)->getResultArray();
    }
}
